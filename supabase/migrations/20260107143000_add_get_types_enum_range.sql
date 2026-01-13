-- Return enum labels as JSON array using enum_range
CREATE OR REPLACE FUNCTION public.get_types(enum_type text)
RETURNS json
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
  json_data json;
  text_query text;
BEGIN
  -- Use %I to safely quote the enum type identifier
  text_query := format('SELECT array_to_json(enum_range(NULL::%I))', enum_type);
  EXECUTE text_query INTO json_data;
  RETURN json_data;
END
$$;
