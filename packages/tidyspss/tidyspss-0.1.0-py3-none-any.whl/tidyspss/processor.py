import os
import logging
import pandas as pd
import numpy as np
import pyreadstat

###############################################################################
# HELPER FUNCTIONS MODULE
###############################################################################

def parse_column_spec_by_data(df, spec):
    """
    Identifies which columns to move given a spec (single col, range, or tuple/list).
    Returns them in the order they appear in df.
    """
    if isinstance(spec, (tuple, list)):
        return list(spec)

    if not isinstance(spec, str):
        logging.warning(f"parse_column_spec_by_data: invalid key '{spec}', not tuple/list/str.")
        return []

    # If it's a single col (no ':'), return it as one
    if ":" not in spec:
        return [spec]

    # It's a range "start_col:end_col"
    left, right = spec.split(":", 1)
    start_col = left.strip()
    end_col = right.strip()

    if start_col not in df.columns:
        logging.warning(f"Start col '{start_col}' not found. Skipping range '{spec}'.")
        return []
    if end_col not in df.columns:
        logging.warning(f"End col '{end_col}' not found. Skipping range '{spec}'.")
        return []

    start_idx = df.columns.get_loc(start_col)
    end_idx = df.columns.get_loc(end_col)
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx

    return df.columns[start_idx : end_idx + 1].tolist()

def reorder_columns_one_shot(df, user_column_position):
    """
    Reorders columns in a single pass for each block of columns to move,
    avoiding multiple df.insert(...) calls.

    user_column_position is a dict:
      key   -> parseable column spec (range, list, single col)
      value -> insertion reference: int (1-based from left or negative from right) or str (existing column name)
    """
    if not user_column_position:
        return df

    for key, value in user_column_position.items():
        # Identify which columns to move
        columns_to_move = parse_column_spec_by_data(df, key)
        if not columns_to_move:
            raise ValueError(f"No valid columns found for '{key}' in user_column_position.")

        # Check for missing columns
        existing_cols = [col for col in columns_to_move if col in df.columns]
        missing_cols = set(columns_to_move) - set(existing_cols)
        if missing_cols:
            raise ValueError(
                f"Cannot reorder columns {missing_cols} because they are not found in DataFrame."
            )

        # Remove these columns
        popped_data = df[existing_cols]
        df = df.drop(columns=existing_cols)

        # Determine insertion position
        if isinstance(value, int):
            if value > 0:
                new_pos = value - 1
            else:
                new_pos = len(df.columns) + value + 1
            new_pos = max(0, min(new_pos, len(df.columns)))
        elif isinstance(value, str):
            if value not in df.columns:
                raise ValueError(f"Cannot reorder after '{value}', it does not exist.")
            ref_idx = df.columns.get_loc(value)
            new_pos = ref_idx + 1
        else:
            raise ValueError(
                f"Value '{value}' must be int (1-based) or str (existing column name)."
            )

        # Rebuild the final column order in a single shot
        left_part = df.columns[:new_pos]
        right_part = df.columns[new_pos:]
        new_col_order = list(left_part) + list(popped_data.columns) + list(right_part)

        # Create the new DataFrame in one shot
        df = pd.concat([df[left_part], popped_data, df[right_part]], axis=1)
        df.columns = new_col_order

    logging.info("Columns reordered (block-based, single-shot).")
    return df

def drop_unwanted_variables(df, user_variable_drop):
    if not user_variable_drop:
        return df
    missing_cols = set(user_variable_drop) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Cannot drop columns that do not exist: {missing_cols}")
    df.drop(columns=user_variable_drop, inplace=True)
    logging.info(f"Dropped columns: {user_variable_drop}")
    return df

def keep_only_variables(df, user_variable_keep):
    if not user_variable_keep:
        return df
    missing_cols = set(user_variable_keep) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Cannot keep columns that do not exist: {missing_cols}")
    
    # Keep only the specified columns, in the order they appear in the original DataFrame
    columns_to_keep = [col for col in df.columns if col in user_variable_keep]
    df_filtered = df[columns_to_keep].copy()
    
    dropped_count = len(df.columns) - len(columns_to_keep)
    logging.info(f"Kept {len(columns_to_keep)} columns, dropped {dropped_count} columns")
    return df_filtered

def rename_variables(df, user_variable_rename):
    if not user_variable_rename:
        return df
    df.rename(columns=user_variable_rename, inplace=True)
    logging.info(f"Renamed columns: {user_variable_rename}")
    return df

def replace_values(df, user_value_replacement):
    if not user_value_replacement:
        return df
    for col in user_value_replacement:
        if col not in df.columns:
            logging.warning(f"Column {col} not in DataFrame; no replacements.")
    df.replace(user_value_replacement, inplace=True)
    logging.info(f"Applied value replacements: {user_value_replacement}")
    return df

def convert_keys_to_numbers_if_possible(value_labels_dict):
    updated = {}
    for k, v in value_labels_dict.items():
        try:
            temp = float(k)
            if temp.is_integer():
                temp = int(temp)
            updated[temp] = v
        except (ValueError, TypeError):
            updated[k] = v
    return updated

def update_variable_labels(meta, user_column_labels):
    if not user_column_labels:
        return {} if not meta else dict(zip(meta.column_names, meta.column_labels))
    if meta is None:
        return user_column_labels
    existing = dict(zip(meta.column_names, meta.column_labels))
    return {**existing, **user_column_labels}

def update_value_labels(meta, user_variable_value_labels):
    if not user_variable_value_labels:
        return {} if (meta is None or not meta.variable_value_labels) else meta.variable_value_labels
    if meta is None:
        return user_variable_value_labels

    existing = meta.variable_value_labels.copy()
    updated = existing.copy()
    for var, lbls in user_variable_value_labels.items():
        conv = convert_keys_to_numbers_if_possible(lbls)
        updated[var] = conv if var in updated else existing.get(var, conv)
    return updated

def update_variable_format(meta, user_variable_format):
    if not user_variable_format:
        return {} if (not meta or not hasattr(meta, "variable_format")) else meta.variable_format
    if not meta or not hasattr(meta, "variable_format"):
        return user_variable_format
    existing = meta.variable_format.copy() if meta.variable_format else {}
    for var, fmt in user_variable_format.items():
        existing[var] = fmt
    return existing

def update_variable_measure(meta, user_variable_measure):
    if not user_variable_measure:
        return {} if not meta else meta.variable_measure.copy()
    if not meta:
        return user_variable_measure
    existing = meta.variable_measure.copy()
    for var, measure in user_variable_measure.items():
        existing[var] = measure
    return existing

def update_variable_display_width(meta, user_variable_display_width):
    if not user_variable_display_width:
        if not meta or not hasattr(meta, "variable_display_width"):
            return {}
        return meta.variable_display_width.copy() if meta.variable_display_width else {}
    if not meta or not hasattr(meta, "variable_display_width"):
        return user_variable_display_width
    existing = meta.variable_display_width.copy() if meta.variable_display_width else {}
    for var, wdth in user_variable_display_width.items():
        existing[var] = wdth
    return existing

def force_string_labels(labels_dict):
    if not labels_dict:
        return {}
    fixed = {}
    for col_name, lbl_val in labels_dict.items():
        col_name_str = str(col_name)
        label_str = str(lbl_val) if lbl_val is not None else ""
        fixed[col_name_str] = label_str
    return fixed

def resolve_missing_ranges(user_missing_ranges, meta):
    if user_missing_ranges is not None:
        return user_missing_ranges
    return getattr(meta, "missing_ranges", None) if meta else None

def resolve_note(user_note, meta):
    if user_note is not None:
        return user_note
    if meta and hasattr(meta, "notes") and meta.notes:
        return "\n".join(meta.notes)
    return None

def resolve_file_label(user_file_label, meta):
    if user_file_label is not None:
        return user_file_label
    return getattr(meta, "file_label", "") if meta else ""

def resolve_compress_settings(user_compress, user_row_compress):
    final_compress = user_compress if user_compress is not None else False
    final_row_compress = user_row_compress if user_row_compress is not None else False
    
    if final_compress and final_row_compress:
        logging.warning("Both `compress` and `row_compress` are True; prioritizing `compress`.")
        final_row_compress = False
    
    return final_compress, final_row_compress

def read_input_file(file_path):
    """
    Reads a file of type SAV (or ZSAV), XLSX, or CSV into a DataFrame.
    If it's SAV/ZSAV, returns (df, meta).
    Otherwise, returns (df, None).
    
    Attempts multiple encodings if the default fails for all file types.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # List of common encodings to try for all file types
    encodings_to_try = [
        None,           # Default (usually UTF-8 or system default)
        'utf-8',        # UTF-8
        'latin1',       # Latin-1 / ISO-8859-1
        'cp1252',       # Windows-1252 (Western European)
        'iso-8859-1',   # ISO-8859-1
        'cp1251',       # Windows-1251 (Cyrillic)
        'cp1250',       # Windows-1250 (Central European)
        'gbk',          # Chinese Simplified
        'big5',         # Chinese Traditional
        'shift_jis',    # Japanese
        'euc-kr',       # Korean
        'utf-16',       # UTF-16
        'utf-32',       # UTF-32
    ]
    
    last_error = None
    
    if ext in [".sav", ".zsav"]:
        # Try different encodings for SAV files
        for encoding in encodings_to_try:
            try:
                if encoding is None:
                    # Try with default encoding
                    df, meta = pyreadstat.read_sav(file_path)
                    logging.info(f"Successfully read SAV file with default encoding")
                else:
                    # Try with specific encoding
                    df, meta = pyreadstat.read_sav(file_path, encoding=encoding)
                    logging.info(f"Successfully read SAV file with encoding: {encoding}")
                return df, meta
            except (UnicodeDecodeError, UnicodeError) as e:
                last_error = e
                if encoding is None:
                    logging.debug(f"Failed to read SAV with default encoding: {str(e)}")
                else:
                    logging.debug(f"Failed to read SAV with encoding {encoding}: {str(e)}")
                continue
            except Exception as e:
                # Some errors might be encoding-related but not explicitly Unicode errors
                last_error = e
                if encoding is None:
                    logging.debug(f"Error reading SAV with default encoding: {str(e)}")
                else:
                    logging.debug(f"Error reading SAV with encoding {encoding}: {str(e)}")
                continue
        
        # If all encodings failed for SAV
        raise ValueError(
            f"Failed to read SAV file '{file_path}' with any of the attempted encodings. "
            f"Last error: {last_error}\n"
            f"You may need to specify a custom encoding or convert the file."
        )
        
    elif ext in [".xls", ".xlsx"]:
        # Try different encodings for Excel files
        for encoding in encodings_to_try:
            try:
                if encoding is None:
                    # Try with default encoding
                    df = pd.read_excel(file_path)
                    logging.info(f"Successfully read Excel file with default encoding")
                else:
                    # Try with specific encoding
                    df = pd.read_excel(file_path, encoding=encoding)
                    logging.info(f"Successfully read Excel file with encoding: {encoding}")
                return df, None
            except (UnicodeDecodeError, UnicodeError) as e:
                last_error = e
                if encoding is None:
                    logging.debug(f"Failed to read Excel with default encoding: {str(e)}")
                else:
                    logging.debug(f"Failed to read Excel with encoding {encoding}: {str(e)}")
                continue
            except Exception as e:
                # Check if it's likely an encoding issue
                error_str = str(e).lower()
                if any(term in error_str for term in ['decode', 'encode', 'codec', 'utf', 'unicode', 'charmap']):
                    last_error = e
                    if encoding is None:
                        logging.debug(f"Error reading Excel with default encoding: {str(e)}")
                    else:
                        logging.debug(f"Error reading Excel with encoding {encoding}: {str(e)}")
                    continue
                else:
                    # If it's not encoding-related, don't try other encodings
                    raise e
        
        # If all encodings failed for Excel
        raise ValueError(
            f"Failed to read Excel file '{file_path}' with any of the attempted encodings. "
            f"Last error: {last_error}\n"
            f"You may need to specify a custom encoding or convert the file."
        )
        
    elif ext == ".csv":
        # Try different encodings for CSV files
        for encoding in encodings_to_try:
            try:
                if encoding is None:
                    # Try with default encoding (usually utf-8)
                    df = pd.read_csv(file_path)
                    logging.info(f"Successfully read CSV file with default encoding")
                else:
                    # Try with specific encoding
                    df = pd.read_csv(file_path, encoding=encoding)
                    logging.info(f"Successfully read CSV file with encoding: {encoding}")
                return df, None
            except (UnicodeDecodeError, UnicodeError) as e:
                last_error = e
                if encoding is None:
                    logging.debug(f"Failed to read CSV with default encoding: {str(e)}")
                else:
                    logging.debug(f"Failed to read CSV with encoding {encoding}: {str(e)}")
                continue
            except Exception as e:
                # Check if it's likely an encoding issue
                error_str = str(e).lower()
                if any(term in error_str for term in ['decode', 'encode', 'codec', 'utf', 'unicode', 'charmap']):
                    last_error = e
                    if encoding is None:
                        logging.debug(f"Error reading CSV with default encoding: {str(e)}")
                    else:
                        logging.debug(f"Error reading CSV with encoding {encoding}: {str(e)}")
                    continue
                else:
                    # If it's not encoding-related (e.g., file not found), don't try other encodings
                    raise e
        
        # If all encodings failed for CSV
        raise ValueError(
            f"Failed to read CSV file '{file_path}' with any of the attempted encodings. "
            f"Last error: {last_error}\n"
            f"You may need to specify a custom encoding or convert the file."
        )
        
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

def process_and_save(df, meta, output_path,
                        user_variable_drop=None,
                        user_value_replacement=None,
                        user_variable_rename=None,
                        user_variable_keep=None,
                        user_column_position=None,
                        user_column_labels=None,
                        user_variable_value_labels=None,
                        user_variable_format=None,
                        user_variable_measure=None,
                        user_variable_display_width=None,
                        user_missing_ranges=None,
                        user_note=None,
                        user_file_label=None,
                        user_compress=None,
                        user_row_compress=None):
    """
    Main processing function that applies all configurations to the DataFrame and saves it.
    Takes a DataFrame that has already been transformed and applies configurations before saving.
    
    IMPORTANT: The processing order is determined by the FUNCTION BODY sequence below,
    NOT by the parameter order in the function call. You can pass parameters in any
    order when calling this function, but the execution will always follow the 
    step-by-step sequence defined in this function body.
    """
    
    if meta is None:
        logging.info("No SPSS metadata found (input is XLSX or CSV).")

    logging.info(f"Starting configuration processing. Initial DataFrame shape: {df.shape}")

    ###########################################################################
    # PROCESSING ORDER: The steps below execute in this EXACT sequence,
    # regardless of the parameter order in your function call.
    ###########################################################################

    # (B) Reordering columns => SINGLE-SHOT approach
    logging.info("(B) Reordering columns...")
    df = reorder_columns_one_shot(df, user_column_position)

    # (C) Dropping unwanted variables
    logging.info("(C) Dropping unwanted variables...")
    drop_unwanted_variables(df, user_variable_drop)

    # (D) Replacing values
    logging.info("(D) Replacing values...")
    replace_values(df, user_value_replacement)

    # (E) Renaming variables
    logging.info("(E) Renaming variables...")
    rename_variables(df, user_variable_rename)

    # (F) Keeping only specified variables
    logging.info("(F) Keeping only specified variables...")
    df = keep_only_variables(df, user_variable_keep)

    # (G-J) Updating metadata
    logging.info("(G) Updating variable and value labels...")
    updated_var_labels = update_variable_labels(meta, user_column_labels)
    updated_val_labels = update_value_labels(meta, user_variable_value_labels)

    logging.info("(H) Updating variable format...")
    updated_format = update_variable_format(meta, user_variable_format)

    logging.info("(I) Updating variable measure...")
    updated_measure = update_variable_measure(meta, user_variable_measure)

    logging.info("(J) Updating display widths...")
    updated_dispwidth = update_variable_display_width(meta, user_variable_display_width)

    # (K) Resolving additional pyreadstat parameters
    logging.info("(K) Resolving additional pyreadstat parameters...")
    final_missing_ranges = resolve_missing_ranges(user_missing_ranges, meta)
    final_note = resolve_note(user_note, meta)
    final_file_label = resolve_file_label(user_file_label, meta)
    final_compress, final_row_compress = resolve_compress_settings(user_compress, user_row_compress)

    rows, cols = df.shape
    logging.info(
        f"(K) FINAL DATAFRAME SHAPE => {rows:,} rows x {cols:,} columns\n"
        f"Saving to: {output_path}\n"
    )

    # Ensure column labels are all strings
    updated_var_labels = force_string_labels(updated_var_labels)

    pyreadstat.write_sav(
        df=df,
        dst_path=output_path,
        file_label=final_file_label,
        column_labels=updated_var_labels,
        compress=final_compress,
        row_compress=final_row_compress,
        note=final_note,
        variable_value_labels=updated_val_labels,
        missing_ranges=final_missing_ranges,
        variable_format=updated_format,
        variable_measure=updated_measure,
        variable_display_width=updated_dispwidth,
    )

    logging.info("SPSS file saved successfully.")
    return df, meta

###############################################################################
# MAIN FUNCTION FOR DIRECT EXECUTION
###############################################################################
def main():
    """
    Main function when running this module directly.
    Users can modify the paths and parameters here for quick testing.
    """
    # Example: the input and output paths
    input_path = r"C:\Path\To\Input\input_file.xlsx"  # can be .sav, .xlsx, or .csv
    output_path = r"C:\Path\To\Output\output_file.sav"
    
    # Read the input file
    df, meta = read_input_file(input_path)
    logging.info(f"Successfully loaded data: {df.shape}")
    
    # Example transformations (modify as needed)
    # df["new_variable"] = 12345
    # df["wave"] = "2024"
    # df["audience"] = np.where(df["S0"].notna(), "Gen Pop", "Panelist")
    
    # User overrides (None by default; one-line examples in comments)
    user_column_position = None                 # e.g. {"Q1_1:Q1_3": "Q1_10", ("demog1","demog2"): 1, "single_col": -1}
    user_column_labels = None                   # e.g. {"Q1": "Question 1", "Q2": "Question 2"}
    user_variable_value_labels = None           # e.g. {"Q1": {1: "Yes", 2: "No"}}
    user_variable_format = None                 # e.g. {"age": "F3.0", "city_name": "A50"}
    user_variable_measure = None                # e.g. {"age": "scale", "city_name": "nominal"}
    user_variable_display_width = None          # e.g. {"city_name": 50, "Q1": 10}
    user_variable_drop = None                   # e.g. ["var1", "var2"]
    user_value_replacement = None               # e.g. {"Q1": {999: 1}, "Q2": {98: 0}}
    user_variable_rename = None                 # e.g. {"old_var": "new_var"}
    user_variable_keep = None                   # e.g. ["Q1", "Q2", "demo_age"] - keeps only these columns
    user_missing_ranges = None                  # e.g. {"Q1": [99], "Q2": [{"lo":998,"hi":999}]}
    user_note = None                            # e.g. "Created on 2025-02-15"
    user_file_label = None                      # e.g. "My Survey 2025"
    user_compress = None                        # e.g. True
    user_row_compress = None                   # e.g. True
    
    try:
        df, meta = process_and_save(
            df=df,
            meta=meta,
            output_path=output_path,
            user_column_position=user_column_position,
            user_column_labels=user_column_labels,
            user_variable_value_labels=user_variable_value_labels,
            user_variable_format=user_variable_format,
            user_variable_measure=user_variable_measure,
            user_variable_display_width=user_variable_display_width,
            user_variable_drop=user_variable_drop,
            user_value_replacement=user_value_replacement,
            user_variable_rename=user_variable_rename,
            user_variable_keep=user_variable_keep,
            user_missing_ranges=user_missing_ranges,
            user_note=user_note,
            user_file_label=user_file_label,
            user_compress=user_compress,
            user_row_compress=user_row_compress
        )
        print(f"Processing complete! Final shape: {df.shape}")
        print(f"File saved to: {output_path}")
    except Exception as exc:
        logging.error("An error occurred in main().", exc_info=True)
        raise

###############################################################################
# CALL main() IF THIS SCRIPT IS RAN DIRECTLY
###############################################################################
if __name__ == "__main__":
    main()