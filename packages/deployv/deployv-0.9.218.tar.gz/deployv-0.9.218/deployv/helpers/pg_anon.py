import csv
import re

TYPES = ['L', 'N', 'A', 'C', 'E']   # literal, number, alpha, alphanumeric, escaped literal


def get_args_pattern(pattern):
    r"""Return format string and parameters from a received pattern.

    Examples:
    - Received pattern: "V\A111FYAAAZZ1" , Result: "VA%sFY%s%s%s", "[1, 3], [2, 3], [3, 2], [1, 1]"
    - Received pattern: "(+52)111-1111111" , Result: "(+52)%s-%s", "[1, 3], [1, 7]"

    Note: this function is somewhat tricky"""   # noqa: W605
    d_mapping = {'1': 'N', 'A': 'A', 'Z': 'C', '\\': 'E'}   # to get proper type value
    arg_list = ''
    arg_str = ''
    prev_ch_type = '*'
    qty = 0
    str_val = ''
    for ch in pattern:
        ch_type = d_mapping.get(ch, 'L')
        if ch_type == prev_ch_type:
            if ch_type in ['N', 'A', 'C']:
                qty += 1
            else:
                str_val += ch
        else:
            if prev_ch_type == 'E':
                ch_type = 'L'
            elif ch_type == 'E':
                pass
            elif prev_ch_type in ['N', 'A', 'C'] and qty:
                arg_str += '%s'
                arg_list += "[%s, %s], " % (TYPES.index(prev_ch_type), qty)
                str_val = ''
            else:
                if prev_ch_type and str_val:
                    arg_str += str_val
                    str_val = ''
                # str_val += ch
            if ch_type == 'L':
                str_val += ch
            elif ch_type in ['N', 'A', 'C']:
                qty = 1
            prev_ch_type = ch_type
        last_ch = ch
    if prev_ch_type == 'E':
        str_val += last_ch
    elif prev_ch_type in ['N', 'A', 'C'] and qty:
        arg_str += '%s'
        arg_list += "[%s, %s], " % (TYPES.index(prev_ch_type), qty)
    else:
        arg_str += str_val
    arg_list = arg_list.strip()
    if arg_list[-1] == ',':
        arg_list = arg_list[:-1]
    return arg_str, arg_list


def get_masking_function(table_name, field_name, field_type, argument):
    """Return SQL query for apply anonymize operation in a field of table

    Examples:
    - Received: "ir_mail_server", "smtp_pass", "alphanumeric", "16"
      Result: SECURITY LABEL FOR anon ON COLUMN ir_mail_server.smtp_pass
              IS 'MASKED WITH FUNCTION anon.random_string(16)';
    - Received: "res_bank", "name", "alpha", "10"
      Result: SECURITY LABEL FOR anon ON COLUMN res_bank.name
              IS 'MASKED WITH FUNCTION vx.random_alpha(10)';
    - Received: "res_partner", "city", "city", None
      Result: SECURITY LABEL FOR anon ON COLUMN res_partner.city
              IS 'MASKED WITH FUNCTION anon.fake_city()'; """
    d_mapping = {'firstname': "FUNCTION anon.fake_first_name()'; ",
                 'lastname': "FUNCTION anon.fake_last_name()'; ",
                 'name': "FUNCTION vx.random_name()'; ",
                 'email': "FUNCTION anon.fake_email()'; ",
                 'country': "FUNCTION anon.fake_country()'; ",
                 'city': "FUNCTION anon.fake_city()'; ",
                 'company': "FUNCTION anon.fake_company()'; "}
    if not table_name or not field_name or not field_type:
        return ''
    field_type = field_type.lower()
    regex_length = re.compile(r'(\d+)')
    regex_range = re.compile(r'(\d+)-(\d+)')
    query = "SECURITY LABEL FOR anon ON COLUMN %s.%s IS 'MASKED WITH " % (table_name, field_name)
    if field_type in ['constantnum', 'constantstr', 'digit', 'alpha', 'alphanumeric', 'pattern'] \
            and not argument:
        return ''
    if field_type == 'constantnum':
        query += "VALUE %s'; " % (argument)
    elif field_type == 'constantstr':
        query += "VALUE ''%s'' '; " % (argument)
    elif field_type == 'digit':
        m_obj = regex_range.match(argument)
        if m_obj and m_obj.group(1) and m_obj.group(2):
            num1 = m_obj.group(1)
            num2 = m_obj.group(2)
        else:
            m_obj = regex_length.match(argument)
            if m_obj and m_obj.group(1):
                qty_digits = int(m_obj.group(1))
                num1 = '1' + ('0' * (qty_digits-1) if (qty_digits-1) else '')
                num2 = '9' * qty_digits
            else:
                return ''
        query += "FUNCTION anon.random_int_between(%s, %s)'; " % (num1, num2)
    elif field_type == 'alpha':
        m_obj = regex_length.match(argument)
        if m_obj and m_obj.group(1):
            query += "FUNCTION vx.random_alpha(%s)'; " % (m_obj.group(1))
        else:
            query = ''
    elif field_type == 'alphanumeric':
        m_obj = regex_length.match(argument)
        if m_obj and m_obj.group(1):
            query += "FUNCTION anon.random_string(%s)'; " % (m_obj.group(1))
        else:
            query = ''
    elif field_type == 'pattern':
        format_str, format_arg_list = get_args_pattern(argument)
        query += "FUNCTION vx.pattern(''%s'', ARRAY [%s])'; " % (format_str, format_arg_list)
    else:
        query += d_mapping.get(field_type, '')
    return query


def get_queries_from_operations_file(filename):
    """Read anonymize operations from a file and return equivalent sql queries"""
    regex = re.compile(r'table:(.*)', re.IGNORECASE)
    queries = []
    query = ''
    table_name = ''
    with open(filename) as fh:
        csv_reader = csv.reader(fh, delimiter=',')
        for row in csv_reader:
            if not row:
                continue
            res = regex.match(row[0])
            if res:
                if query and table_name:
                    query += "SELECT anon.anonymize_table('%s');" % (table_name)
                    queries.append(query)
                query = ''
                table_name = res.group(1)
                table_name = table_name.strip()
                continue
            field_name = row[0]
            field_type = row[1]
            if len(row) > 2:
                argument = row[2]
            else:
                argument = None
            if table_name:
                query += get_masking_function(table_name, field_name, field_type, argument)
        if query and table_name:
            query += "SELECT anon.anonymize_table('%s');" % (table_name)
            queries.append(query)
    return queries


def get_queries_vx_functions():
    return """CREATE OR REPLACE FUNCTION vx.random_alpha(k integer)
    RETURNS varchar AS
    $$
    DECLARE res varchar;
    BEGIN
    SELECT array_to_string(array(
    SELECT substr('ABCDEFGHIJKLMNOPQRSTUVWXYZ',((random()*(26-k)+1)::integer) ,1)
    FROM generate_series(1, k)
    ), '') INTO res;
    RETURN res;
    END
    $$
    LANGUAGE PLPGSQL
    VOLATILE
    RETURNS NULL ON NULL INPUT
    SECURITY INVOKER
    SET search_path='';
    CREATE OR REPLACE FUNCTION vx.random_digit(k integer)
    RETURNS varchar AS
    $$
    DECLARE res varchar;
    BEGIN
    SELECT array_to_string(array(
    SELECT substr('0123456789',((random()*(10-k)+1)::integer) ,1) FROM generate_series(1, k)
    ), '') INTO res;
    RETURN res;
    END
    $$
    LANGUAGE PLPGSQL
    VOLATILE
    RETURNS NULL ON NULL INPUT
    SECURITY INVOKER
    SET search_path='';
    CREATE OR REPLACE FUNCTION vx.random_name()
    RETURNS varchar AS
    $$
    DECLARE res varchar;
    BEGIN
    SELECT anon.fake_first_name() || ' ' || anon.fake_last_name() INTO res;
    RETURN res;
    END
    $$
    LANGUAGE PLPGSQL
    VOLATILE
    RETURNS NULL ON NULL INPUT
    SECURITY INVOKER
    SET search_path='';
    CREATE OR REPLACE FUNCTION vx.gen_random_str(ch_type integer, ch_qty integer)
    RETURNS varchar AS
    $$
    DECLARE res varchar;
    BEGIN
    if ch_type = 1 then
    res := vx.random_digit(ch_qty);
    elsif ch_type = 2 then
    res := vx.random_alpha(ch_qty);
    elsif ch_type = 3 then
    res := anon.random_string(ch_qty);
    else
    res := '';
    end if;
    RETURN res;
    END
    $$
    LANGUAGE PLPGSQL
    VOLATILE
    RETURNS NULL ON NULL INPUT
    SECURITY INVOKER
    SET search_path='';
    CREATE OR REPLACE FUNCTION vx.pattern(format_str varchar, params integer[][])
    RETURNS varchar AS
    $$
    DECLARE
    args varchar[];
    res varchar;
    BEGIN
    FOR i IN 1..array_length(params, 1)
    LOOP
    args := array_append(args, vx.gen_random_str(params[i][1], params[i][2]));
    END LOOP;
    SELECT format(format_str, VARIADIC args) INTO res;
    RETURN res;
    END
    $$
    LANGUAGE PLPGSQL
    VOLATILE
    RETURNS NULL ON NULL INPUT
    SECURITY INVOKER
    SET search_path='';"""
