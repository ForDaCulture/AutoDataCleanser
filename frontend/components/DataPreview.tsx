import React from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface DataPreviewProps {
  data: any[];
  title: string;
}

export default function DataPreview({ data, title }: DataPreviewProps) {
  const columnDefs = React.useMemo(() => {
    if (!data.length) return [];
    return Object.keys(data[0]).map(key => ({
      field: key,
      sortable: true,
      filter: true,
      resizable: true,
    }));
  }, [data]);

  const defaultColDef = {
    flex: 1,
    minWidth: 100,
    filter: true,
    sortable: true,
  };

  return (
    <div className="w-full h-[500px] p-4">
      <h3 className="text-xl font-semibold mb-4">{title}</h3>
      <div className="ag-theme-alpine w-full h-full">
        <AgGridReact
          rowData={data}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          pagination={true}
          paginationPageSize={10}
          animateRows={true}
        />
      </div>
    </div>
  );
} 