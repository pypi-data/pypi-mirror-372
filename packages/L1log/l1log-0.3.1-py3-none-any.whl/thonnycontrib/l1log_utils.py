def is_joker(binome_name :str) -> bool:
    """
    Return True if binome_name is accepted as a joker. 
    Jokers are 6 characters long strings that :
    - begin with MI
    - followed by an int group number in [11, 15] U [21, 24]  
    - followed by 2 digits
    """
    group = binome_name[2:4]
    number = binome_name[4:6]
    return len(binome_name) == 6 \
        and  binome_name[0:2] == 'MI' \
        and  ('11' <= group <= '15' or '21' <= group <= '24') \
        and number[0].isdigit() and number[1].isdigit()
            
def is_identifier_accepted(binome_name:str, ldap_identifiers:list[str]) -> bool:
    return binome_name == '' \
        or ldap_identifiers != None and binome_name in ldap_identifiers \
        or is_joker(binome_name)
