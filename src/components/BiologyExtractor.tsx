
import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, AlertCircle, Link } from "lucide-react";
import { toast } from "sonner";
import JsonViewer from "./JsonViewer";
import { extractBiologyInfo } from "@/services/extractionService";
import { isValidUrl, isUrlEmpty } from "@/lib/validations";

const BiologyExtractor: React.FC = () => {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);
  
  const handleExtract = async () => {
    // Reset states
    setError(null);
    setResult(null);
    
    // Validate URL
    if (isUrlEmpty(url)) {
      setError("Please enter a URL");
      return;
    }
    
    if (!isValidUrl(url)) {
      setError("Please enter a valid URL");
      return;
    }
    
    // Extract biology information
    try {
      setIsLoading(true);
      const data = await extractBiologyInfo(url);
      setResult(data);
      toast.success("Biology information extracted successfully!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
      toast.error("Failed to extract biology information");
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card className="w-full max-w-2xl shadow-lg">
      <CardHeader className="border-b">
        <CardTitle className="text-biology">Biology Information Extractor</CardTitle>
        <CardDescription>
          Paste an article URL to extract biology-related information
        </CardDescription>
      </CardHeader>
      
      <CardContent className="pt-6">
        <div className="flex flex-col gap-4">
          <div className="flex gap-2">
            <div className="relative flex-grow">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-400">
                <Link size={18} />
              </div>
              <Input 
                type="url" 
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste article URL here"
                className="pl-10"
                disabled={isLoading}
              />
            </div>
            <Button 
              onClick={handleExtract}
              disabled={isLoading}
              className="bg-biology hover:bg-biology-dark"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Extracting...
                </>
              ) : (
                "Extract Biology Info"
              )}
            </Button>
          </div>
          
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {result && (
            <div className="mt-4 p-4 bg-gray-50 rounded-md">
              <div className="text-sm font-medium text-gray-500 mb-2">Results:</div>
              <JsonViewer data={result} expanded={true} />
            </div>
          )}
        </div>
      </CardContent>
      
      <CardFooter className="border-t bg-gray-50 text-xs text-gray-500">
        <p>This tool extracts biology information from scientific articles and web pages.</p>
      </CardFooter>
    </Card>
  );
};

export default BiologyExtractor;
