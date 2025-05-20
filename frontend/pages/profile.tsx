import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getProfile } from '../utils/api';
import type { ProfileResult } from '../types/api';
import DataPreview from '../components/DataPreview';

export default function Profile() {
  const router = useRouter();
  const { session_id } = router.query;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ProfileResult | null>(null);

  useEffect(() => {
    if (!session_id) return;

    const fetchProfile = async () => {
      try {
        // Try to get preview data from localStorage first
        const cachedPreview = localStorage.getItem(`preview_${session_id}`);
        if (cachedPreview) {
          const cachedData = JSON.parse(cachedPreview);
          setData(cachedData);
        }

        const profileData = await getProfile(session_id as string);
        if (profileData.success) {
          setData(profileData);
          // Cache the preview data
          localStorage.setItem(`preview_${session_id}`, JSON.stringify(profileData));
        } else {
          throw new Error('Failed to load profile data');
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load profile data');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [session_id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => router.push('/upload')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Data Profile</h1>
          <div className="text-sm text-gray-600">
            <p>Total Rows: {data.rows.toLocaleString()}</p>
            <p>Total Columns: {data.columns.length}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {data.profile.map((stat) => (
            <div
              key={stat.column}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {stat.column}
              </h3>
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  Type: <span className="font-medium">{stat.type}</span>
                </p>
                <p className="text-sm text-gray-600">
                  Missing Values: <span className="font-medium">{stat.missing_pct.toFixed(1)}%</span>
                </p>
                <p className="text-sm text-gray-600">
                  Unique Values: <span className="font-medium">{stat.unique_count.toLocaleString()}</span>
                </p>
                {stat.mean !== undefined && (
                  <p className="text-sm text-gray-600">
                    Mean: <span className="font-medium">{stat.mean.toFixed(2)}</span>
                  </p>
                )}
                {stat.std !== undefined && (
                  <p className="text-sm text-gray-600">
                    Std Dev: <span className="font-medium">{stat.std.toFixed(2)}</span>
                  </p>
                )}
                {stat.min !== undefined && (
                  <p className="text-sm text-gray-600">
                    Min: <span className="font-medium">{stat.min}</span>
                  </p>
                )}
                {stat.max !== undefined && (
                  <p className="text-sm text-gray-600">
                    Max: <span className="font-medium">{stat.max}</span>
                  </p>
                )}
                {stat.min_length !== undefined && (
                  <p className="text-sm text-gray-600">
                    Min Length: <span className="font-medium">{stat.min_length}</span>
                  </p>
                )}
                {stat.max_length !== undefined && (
                  <p className="text-sm text-gray-600">
                    Max Length: <span className="font-medium">{stat.max_length}</span>
                  </p>
                )}
                {stat.avg_length !== undefined && (
                  <p className="text-sm text-gray-600">
                    Avg Length: <span className="font-medium">{stat.avg_length.toFixed(1)}</span>
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <DataPreview data={data.preview} title="Data Preview" />
        </div>

        <div className="mt-8 flex justify-end space-x-4">
          <button
            onClick={() => router.push('/upload')}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Upload New File
          </button>
          <button
            onClick={() => router.push(`/result?session_id=${session_id}`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Proceed to Cleaning
          </button>
        </div>
      </div>
    </div>
  );
} 