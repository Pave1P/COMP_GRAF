def get_issuer(number):
    n=str(number)
    if (n[:2] in '34' or n[:2] in '37') and len(n)==15:
        print('AMEX')
    elif n[:4] in '6011' and len(n)==16:
        print('Discover')
    elif (n[:2] in '51' or n[:2] in '52' or n[:2] in '53' or n[:2] in '54' or n[:2] in '55') and len(n)==16:
        print('Mastercard ')
    elif (n[0]=='4' and (len(n)==13 or len(n)==16)):
        print('VISA')
    else:print('Unknown')
get_issuer(6011783664441608)