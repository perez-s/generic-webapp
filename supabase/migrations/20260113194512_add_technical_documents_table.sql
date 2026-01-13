-- Create technical_documents table for storing document metadata
CREATE TABLE IF NOT EXISTS public.technical_documents (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name text NOT NULL UNIQUE,
  description text,
  original_filename text NOT NULL,
  stored_filename text NOT NULL,
  file_path text NOT NULL,
  uploaded_by text NOT NULL,
  year smallint NOT NULL,
  month smallint NOT NULL,
  uploaded_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_by text,
  file_size bigint NOT NULL,
  mime_type text
);

-- Add trigger for automatic updated_at timestamp
CREATE TRIGGER update_technical_documents_updated_at
  BEFORE UPDATE ON public.technical_documents
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Add indexes for better query performance
CREATE INDEX idx_technical_documents_name ON public.technical_documents(name);
CREATE INDEX idx_technical_documents_uploaded_by ON public.technical_documents(uploaded_by);
CREATE INDEX idx_technical_documents_uploaded_at ON public.technical_documents(uploaded_at DESC);

-- Add comment for documentation
COMMENT ON TABLE public.technical_documents IS 'Stores metadata for technical documents uploaded by users';
