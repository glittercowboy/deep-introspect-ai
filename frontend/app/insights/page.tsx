"use client"

import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { KnowledgeGraph } from '@/components/insights/knowledge-graph';
import { UserSummary } from '@/components/insights/summary-card';
import * as api from '@/lib/api';
import Link from 'next/link';
import { Brain, LucideHome, ArrowLeft, RefreshCw } from 'lucide-react';

export default function InsightsPage() {
  const [activeTab, setActiveTab] = useState<string>('summary');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const { toast } = useToast();

  useEffect(() => {
    const loadInsights = async () => {
      setIsLoading(true);
      try {
        // Load user summary
        const summaryData = await api.getUserSummary();
        setSummary(summaryData);

        // Load knowledge graph
        const graphData = await api.getKnowledgeGraph();
        setGraphData(graphData);
      } catch (error) {
        console.error('Failed to load insights:', error);
        toast({
          title: 'Error',
          description: 'Failed to load insights. Please try again.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadInsights();
  }, [toast]);

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      // Refresh insights
      toast({
        title: 'Refreshing',
        description: 'Generating new insights based on your conversations...',
      });

      // These would typically trigger re-generation on the backend
      const summaryData = await api.getUserSummary();
      setSummary(summaryData);

      const graphData = await api.getKnowledgeGraph();
      setGraphData(graphData);

      toast({
        title: 'Insights Updated',
        description: 'Your insights have been refreshed with the latest data.',
      });
    } catch (error) {
      console.error('Failed to refresh insights:', error);
      toast({
        title: 'Error',
        description: 'Failed to refresh insights. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container max-w-7xl mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Link href="/">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">Personal Insights</h1>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh Insights
          </Button>
          <Button asChild>
            <Link href="/chat">
              Start Chatting
            </Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="summary" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="summary">
            <Brain className="mr-2 h-4 w-4" />
            Profile Summary
          </TabsTrigger>
          <TabsTrigger value="knowledge-graph">
            <LucideHome className="mr-2 h-4 w-4" />
            Knowledge Graph
          </TabsTrigger>
        </TabsList>
        <TabsContent value="summary" className="mt-6">
          <UserSummary
            data={summary}
            isLoading={isLoading}
          />
        </TabsContent>
        <TabsContent value="knowledge-graph" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Personal Knowledge Graph</CardTitle>
              <CardDescription>
                A visual representation of concepts, beliefs, and patterns extracted from your conversations.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center p-0 h-[600px]">
              <KnowledgeGraph
                data={graphData}
                isLoading={isLoading}
                width={800}
                height={600}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
