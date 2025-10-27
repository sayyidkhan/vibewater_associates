import ResearchAgent from '../../components/ResearchAgent';

export default function ResearchPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">AI Research Agent</h1>
        <p className="text-gray-600">
          Discover high-performance trading strategies using autonomous AI research and backtesting.
        </p>
      </div>
      
      <ResearchAgent />
    </div>
  );
}