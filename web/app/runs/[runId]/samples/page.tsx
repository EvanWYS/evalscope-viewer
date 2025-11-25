import Link from 'next/link';
import { getSamples, getRunMeta, getRunsIndex } from '@/lib/dataLoader';
import { SamplesTable } from '@/components/SamplesTable';

interface PageProps {
  params: Promise<{ runId: string }>;
  searchParams: Promise<{ dataset?: string }>;
}

// Generate static paths for all runs
export async function generateStaticParams() {
  try {
    const index = await getRunsIndex();
    return index.runs.map((run) => ({
      runId: run.run_id,
    }));
  } catch (error) {
    console.error('Failed to generate static params:', error);
    return [];
  }
}

export default async function SamplesPage({ params, searchParams }: PageProps) {
  const { runId } = await params;
  const { dataset } = await searchParams;

  let meta;
  let samples;
  let error = null;

  try {
    meta = await getRunMeta(runId);

    if (!dataset) {
      error = 'No dataset specified';
    } else {
      samples = await getSamples(runId, dataset);
    }
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load samples';
  }

  if (error || !meta || !samples) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800 mb-2">
            Error Loading Samples
          </h2>
          <p className="text-red-700">{error}</p>
          <Link
            href={`/runs/${runId}`}
            className="text-blue-600 hover:underline mt-4 inline-block"
          >
            ← Back to run details
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-6">
        <Link
          href={`/runs/${runId}`}
          className="text-blue-600 hover:underline text-sm"
        >
          ← Back to run details
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Sample Predictions
            </h1>
            <p className="text-gray-600">
              {meta.model.name} - {dataset}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Total Samples</p>
            <p className="text-2xl font-bold text-gray-900">
              {samples.length}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {meta.datasets.map((d) => (
            <Link
              key={d}
              href={`/runs/${runId}/samples?dataset=${d}`}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                d === dataset
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {d}
            </Link>
          ))}
        </div>
      </div>

      <SamplesTable samples={samples} />
    </div>
  );
}
