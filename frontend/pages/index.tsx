import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '../utils/supabaseClient';
import Auth from '../components/Auth';

export default function Home() {
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setSession(session);
      setLoading(false);

      if (session) {
        router.push('/upload');
      }
    };

    getSession();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AutoDataCleanser
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Clean and transform your data with ease
          </p>
        </div>

        <div className="max-w-md mx-auto">
          <Auth />
        </div>
      </div>
    </div>
  );
} 