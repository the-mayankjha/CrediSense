import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { UploadCloud, Search, FileText, CheckCircle, AlertTriangle, ArrowLeft } from 'lucide-react';

export default function Assessment() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  
  // State for data from each step
  const [file, setFile] = useState<File | null>(null);
  const [ingestData, setIngestData] = useState<any>(null);
  const [researchData, setResearchData] = useState<any>(null);
  const [primaryInsights, setPrimaryInsights] = useState('');
  const [camData, setCamData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // --- Step 1: Upload & Ingest ---
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const submitDocument = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.uploadDocument(file);
      if (resp.status === 'success') {
        setIngestData(resp.data);
        setStep(2);
      } else {
        setError('Failed to extract data.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  // --- Step 2: Research ---
  const runResearch = async () => {
    if (!ingestData?.company_name) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.researchCompany(ingestData.company_name);
      if (resp.status === 'success') {
        setResearchData(resp.data);
        setStep(3);
      } else {
        setError('Research failed.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research failed');
    } finally {
      setLoading(false);
    }
  };

  // --- Step 3: primary insights -> CAM ---
  const generateCAM = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        application_id: `APP-${Date.now()}`,
        company_data: ingestData,
        research_data: researchData,
        primary_insights: primaryInsights || 'No primary insights provided.'
      };
      const resp = await api.generateCAM(payload);
      if (resp.status === 'success') {
        setCamData(resp.data);
        setStep(4);
      } else {
        setError('CAM generation failed.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'CAM generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button 
        onClick={() => navigate('/')} 
        className="flex items-center text-sm font-medium text-slate-500 hover:text-slate-700 mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
      </button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">New Credit Assessment</h1>
        <p className="mt-2 text-slate-500">Processing via AI Recommendation Engine</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-start">
          <AlertTriangle className="h-5 w-5 mr-3 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Stepper Wizard (could be broken out, but kept inline for simplicity) */}
      
      {step === 1 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <UploadCloud className="mr-2 h-6 w-6 text-blue-600" /> Step 1: Document Ingestion
          </h2>
          <p className="text-slate-600 mb-4">Upload a recent financial report or prospectus (PDF) for the applicant company.</p>
          
          <div className="border-2 border-dashed border-slate-300 p-8 rounded-md text-center bg-slate-50">
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleFileUpload} 
              className="block w-full text-sm text-slate-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100 mb-4 mx-auto"
            />
            {file && <p className="text-sm text-slate-700 font-medium">Selected: {file.name}</p>}
          </div>

          <div className="mt-6 flex justify-end">
            <button 
              onClick={submitDocument} 
              disabled={!file || loading}
              className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Extracting Data...' : 'Extract Data & Continue'}
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
           <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Search className="mr-2 h-6 w-6 text-blue-600" /> Step 2: Risk Research
          </h2>
          <div className="mb-6 p-4 bg-slate-50 rounded border border-slate-200">
            <h3 className="font-medium text-slate-700">Extracted Company details:</h3>
            <p className="text-lg font-bold text-slate-900 mt-1">{ingestData?.company_name}</p>
            {ingestData?.identified_risks && (
              <p className="text-sm text-slate-600 mt-2">Found {ingestData.identified_risks.length} initial risk points from document.</p>
            )}
          </div>
          <p className="text-slate-600 mb-6">We will now dispatch the Research Agent to search the internet for recent news, MCA filings, and regulatory updates regarding this company.</p>
          
          <div className="flex justify-end">
            <button 
              onClick={runResearch} 
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Researching web...' : 'Run Web Research'}
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
           <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FileText className="mr-2 h-6 w-6 text-blue-600" /> Step 3: Primary Insights & CAM
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
             <div className="p-4 bg-slate-50 rounded border border-slate-200">
                 <h3 className="font-medium text-slate-700 mb-2">Ingestion Summary</h3>
                 <p className="text-sm text-slate-900"><strong>Company:</strong> {ingestData?.company_name}</p>
                 <p className="text-sm text-slate-600 mt-1">{ingestData?.identified_risks?.length || 0} risks extracted.</p>
             </div>
             <div className="p-4 bg-slate-50 rounded border border-slate-200">
                 <h3 className="font-medium text-slate-700 mb-2">Research Summary</h3>
                 <p className="text-sm text-slate-900"><strong>Sentiment:</strong> {researchData?.overall_sentiment}</p>
                 <p className="text-sm text-slate-600 mt-1">{researchData?.risk_alerts?.length || 0} external risk alerts found.</p>
             </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-2">Primary Officer Insights (Optional)</label>
            <textarea 
              rows={4}
              value={primaryInsights}
              onChange={e => setPrimaryInsights(e.target.value)}
              className="w-full border-slate-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-3 border"
              placeholder="Enter any qualitative context, previous relationship history, or mitigating factors that the AI should consider..."
            />
          </div>
          
          <div className="flex justify-end">
            <button 
              onClick={generateCAM} 
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Synthesizing CAM...' : 'Generate 5 Cs Report'}
            </button>
          </div>
        </div>
      )}

      {step === 4 && camData && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
           <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-slate-900 flex items-center">
                <CheckCircle className="mr-3 h-8 w-8 text-green-500" /> Final Credit Appraisal Memo
              </h2>
              <span className={`px-4 py-1 rounded-full text-sm font-bold ${camData.overall_decision === 'Approve' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {camData.overall_decision}
              </span>
           </div>

           <div className="mb-8 grid grid-cols-2 gap-4">
              <div className="bg-slate-50 p-4 rounded border border-slate-200">
                 <p className="text-sm text-slate-500 mb-1">Suggested Limit</p>
                 <p className="text-2xl font-bold text-slate-900">₹{camData.suggested_limit_cr} Cr</p>
              </div>
              <div className="bg-slate-50 p-4 rounded border border-slate-200">
                 <p className="text-sm text-slate-500 mb-1">Risk Premium</p>
                 <p className="text-2xl font-bold text-slate-900">+{camData.interest_rate_premium_bps} bps</p>
              </div>
           </div>

           <div className="mb-8 p-5 bg-blue-50 border border-blue-100 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Logic Explanation</h3>
              <p className="text-blue-800 text-sm leading-relaxed">{camData.explainable_logic}</p>
           </div>

           <h3 className="text-lg font-bold text-slate-900 mb-4 border-b pb-2">The 5 Cs of Credit</h3>
           <div className="space-y-4 mb-8">
              {Object.entries(camData.five_cs_summary || {}).map(([key, value]) => (
                <div key={key} className="flex">
                  <div className="w-32 flex-shrink-0 font-semibold text-slate-700 capitalize">{key}</div>
                  <div className="text-slate-600 text-sm">{value as string}</div>
                </div>
              ))}
           </div>

           {camData.key_risk_mitigants && camData.key_risk_mitigants.length > 0 && (
             <>
               <h3 className="text-lg font-bold text-slate-900 mb-4 border-b pb-2">Key Risk Mitigants</h3>
               <ul className="list-disc pl-5 space-y-1 text-slate-600 text-sm mb-8">
                  {camData.key_risk_mitigants.map((mitigant: string, i: number) => (
                    <li key={i}>{mitigant}</li>
                  ))}
               </ul>
             </>
           )}

            <div className="flex justify-between border-t border-slate-200 pt-6">
               <button 
                  onClick={() => navigate('/')}
                  className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
                >
                  Return to Dashboard
                </button>
               <button 
                  className="px-4 py-2 bg-slate-900 text-white rounded hover:bg-slate-800 font-medium"
                >
                  Forward to Credit Committee
                </button>
            </div>
        </div>
      )}

    </div>
  );
}
