import ldap

# TODO et on fait quoi si pb avec search_s ?
def get_identifiers(ldap_connection) -> list[str]:
    '''
    Calls search_s on ldap_connection then extracts list of membership 
    and returns it.
    '''
    response_list =  ldap_connection.search_s('ou=groups,dc=fil.univ-lille,dc=fr',ldap.SCOPE_SUBTREE,'(cn=l1)',["memberUid"])
    response = response_list[0]
    attrs = response[1] # response is of the form (dn, attrs), where dn is a string containing the DN (distinguished name) of the entry, and attrs is a dictionary containing the attributes associated with the entry. The keys of attrs are strings, and the associated values are lists of strings.
    if attrs == {}:
        identifiers = []
    else:
        identifiers_bytes = attrs["memberUid"]
        identifiers = [id.decode() for id in identifiers_bytes]
    return identifiers

     
