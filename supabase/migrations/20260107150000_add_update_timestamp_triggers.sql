-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for providers table
CREATE TRIGGER update_providers_updated_at
BEFORE UPDATE ON public.providers
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create trigger for allies table
CREATE TRIGGER update_allies_updated_at
BEFORE UPDATE ON public.allies
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create trigger for requests table
CREATE TRIGGER update_requests_updated_at
BEFORE UPDATE ON public.requests
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create trigger for pickup table
CREATE TRIGGER update_pickup_updated_at
BEFORE UPDATE ON public.pickup
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create trigger for residues_collected table
CREATE TRIGGER update_residues_collected_updated_at
BEFORE UPDATE ON public.residues_collected
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();
