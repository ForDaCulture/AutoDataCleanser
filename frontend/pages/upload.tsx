import { useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import type { NextPage } from 'next';
import { useDropzone, FileRejection, DropzoneOptions } from 'react-dropzone';
import { uploadFile } from '../utils/api';
import type { UploadResult, ProfileResult } from '../types/api';

const Upload: NextPage = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [result, setResult] = useState<UploadResult | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0];
      setError(error.message);
      return;
    }

    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    const fileSize = file.size / (1024 * 1024); // Convert to MB

    if (fileSize > 10) {
      setError('File size must be less than 10MB');
      return;
    }

    setLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const uploadResult = await uploadFile(file, (progress) => {
        setUploadProgress(progress);
      });
      
      if (uploadResult.success) {
        setResult(uploadResult);
        // Store preview data in localStorage for the profile page
        const previewData: Partial<ProfileResult> = {
          success: true,
          preview: uploadResult.preview,
          columns: uploadResult.columns,
          rows: uploadResult.rows,
          profile: [] // Will be populated by the profile page
        };
        localStorage.setItem(`preview_${uploadResult.session_id}`, JSON.stringify(previewData));
        router.push(`/profile?session_id=${uploadResult.session_id}`);
      } else {
        throw new Error('Upload failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload file');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  }, [router]);

  const dropzoneOptions: DropzoneOptions = {
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone(dropzoneOptions);

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Upload Your Data File
          </h1>
          <p className="text-gray-600 mb-8">
            Upload your CSV or Excel file to begin the data cleaning process.
            We'll analyze your data and suggest cleaning operations.
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`mt-8 p-12 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-500'}
            ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} disabled={loading} />
          <div className="space-y-4">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="text-gray-600">
              {isDragActive ? (
                <p>Drop the file here...</p>
              ) : loading ? (
                <p>Uploading...</p>
              ) : (
                <p>
                  Drag and drop your CSV or Excel file here, or click to select a file
                </p>
              )}
            </div>
            <p className="text-sm text-gray-500">
              Supported formats: CSV, Excel (.xlsx, .xls)
              <br />
              Maximum file size: 10MB
            </p>
          </div>
        </div>

        {loading && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="mt-2 text-center text-gray-600">Uploading... {uploadProgress}%</p>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload; 