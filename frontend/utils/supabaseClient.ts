import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://wphdrdnzpxgpdjhirirr.supabase.co';
const supabaseAnonKey = 'USE_REAL_KEY_OR_ASK';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export const getSession = async () => {
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error) {
    console.error('Error getting session:', error.message);
    return null;
  }
  return session;
};

export const getJWT = async () => {
  const session = await getSession();
  return session?.access_token;
}; 