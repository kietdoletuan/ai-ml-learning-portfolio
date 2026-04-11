readings = [
    23.5, None, 45.2, 12.0, None, 67.8, 34.1, -999, None, 56.3, 78.9, None, 90.0, -999, 12.5, 150.0, 32.4, None, 45.6, 67.8, None, 89.0, -999, 23.4, None, 56.7, 78.9, None, 90.1, -999, 12.6, 150.1
]

VALID_RANGE = (0.0, 100.0)
ERROR_CODE = -999

nulls_count = 0
total = 0
min_val = float('inf')
max_val = float('-inf')
errors_count = 0
oors_count = 0
valids_count = 0
readings_count = 0

format_string1 = "{:<20} {:<10} {:<20}"
format_string2 = "{:<20} {:<10}"


for reading in readings:
    
    readings_count += 1
    
    if reading is None:
        
        nulls_count += 1
        
    elif reading == ERROR_CODE:
        
        errors_count += 1
    
    elif reading < VALID_RANGE[0] or reading > VALID_RANGE[1]:
        oors_count += 1
    else:                       
        valids_count += 1
        total += reading
        if reading > max_val:
            max_val = reading
        if reading < min_val:
            min_val = reading

print("=== SENSOR DATA QUALITY REPORT ===")
print(f"Total readings   : {readings_count}")
print(f"VALID            : {valids_count} ({valids_count/readings_count*100:.1f}%)")
print(f"NULL             : {nulls_count} ({nulls_count/readings_count*100:.1f}%)")
print(f"ERROR_CODE       : {errors_count} ({errors_count/readings_count*100:.1f}%)")
print(f"OUT_OF_RANGE     : {oors_count} ({oors_count/readings_count*100:.1f}%)")
print()
print(f"Mean (valid only): {total/valids_count:.2f}")
print(f"Min  (valid only): {min_val:.1f}")
print(f"Max  (valid only): {max_val:.1f}")


