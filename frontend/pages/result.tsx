import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { cleanData, getAudit, downloadFile } from '../utils/api';
import type { CleanResult, AuditLog } from '../types/api';
import DataPreview from '../components/DataPreview';

export default function Result() {
  const router = useRouter();
  const { session_id } = router.query;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cleanResult, setCleanResult] = useState<CleanResult | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [downloadLoading, setDownloadLoading] = useState(false);

  useEffect(() => {
    if (!session_id) return;

    const processData = async () => {
      try {
        // Clean the data
        const result = await cleanData(session_id as string, {
          impute_missing: true,
          remove_outliers: true,
          deduplicate: true,
        });
        setCleanResult(result);

        // Get audit logs
        const auditResult = await getAudit(session_id as string);
        setAuditLogs(auditResult.logs);
      } catch (err: any) {
        setError(err.message || 'Failed to process data');
      } finally {
        setLoading(false);
      }
    };

    processData();
  }, [session_id]);

  const handleDownload = async () => {
    if (!session_id) return;

    setDownloadLoading(true);
    try {
      const blob = await downloadFile(session_id as string);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cleaned_data.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || 'Failed to download file');
    } finally {
      setDownloadLoading(false);
    }
  };

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
          </div>
        </div>
      </div>
    );
  }

  if (!cleanResult) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Cleaned Data</h1>
          <button
            onClick={handleDownload}
            disabled={downloadLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {downloadLoading ? 'Downloading...' : 'Download Cleaned Data'}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
          <DataPreview data={cleanResult.data} title="Cleaned Data Preview" />
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Transformation History</h2>
          <div className="space-y-4">
            {auditLogs.map((log, index) => (
              <div
                key={index}
                className="flex items-start space-x-4 p-4 bg-gray-50 rounded-md"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{log.action}</p>
                  <p className="text-sm text-gray-600">{log.details}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(log.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 flex justify-end">
          <button
            onClick={() => router.push('/upload')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Process Another File
          </button>
        </div>
      </div>
    </div>
  );
} 