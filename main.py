    full_pattern = r"(\d+\.\d+\.\d+\.\d+)(?:\s*-\s*(\d+\.\d+\.\d+\.\d+))?\s+port:\s*(\d+)(?:\s*-\s*(\d+))?"
    
    match = re.match(full_pattern, input_str.strip())
    
    if not match:
        return None
    
    dst_ip = match.group(1)
    dst_ip_last = match.group(2) if match.group(2) else None
    port = int(match.group(3))
    port_last = int(match.group(4)) if match.group(4) else None