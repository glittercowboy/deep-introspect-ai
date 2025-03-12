"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { createClientComponentClient } from "@supabase/supabase-js";
import { formatDate } from "@/lib/utils";
import { SparklesCore } from "@/components/ui/aceternity/sparkles";
import MainNav from "@/components/layout/main-nav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { 
  BrainCircuit, 
  Lightbulb, 
  Network, 
  Search, 
  Filter, 
  Download, 
  Share2, 
  TagIcon,
  Calendar 
} from "lucide-react";
import ForceGraph2D from 'react-force-graph';

// Types
interface Insight {
  id: string;
  type: string;
  content: string;
  created_at: string;
  conversation_id: string;
  evidence: string;
}

interface GraphNode {
  id: string;
  label: string;
  type: string;
  content?: string;
  evidence?: string;
  color?: string;
  size?: number;
}

interface GraphLink {
  source: string;
  target: string;
  label?: string;
  color?: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface UserSummary {
  summary: string;
  categories: {
    traits: string;
    values_beliefs: string;
    goals_aspirations: string;
    challenges: string;
    patterns: string;
  };
}

export default function InsightsPage() {
  const router = useRouter();
  const { toast } = useToast();
  const supabase = createClientComponentClient();
  const graphRef = useRef<any>(null);
  
  const [isLoading, setIsLoading] = useState(true);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [userSummary, setUserSummary] = useState<UserSummary | null>(null);
  const [selectedInsightType, setSelectedInsightType] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState("list");

  // Generate node color based on type
  const getNodeColor = (type: string) => {
    const colors: Record<string, string> = {
      user: "#FCD34D", // amber-300
      belief: "#60A5FA", // blue-400
      value: "#9333EA", // purple-600
      pattern: "#F97316", // orange-500
      trait: "#10B981", // emerald-500
      goal: "#4F46E5", // indigo-600
      challenge: "#EF4444", // red-500
      concept: "#6366F1", // indigo-500
      entity: "#8B5CF6", // violet-500
    };
    
    return colors[type.toLowerCase()] || "#94A3B8"; // slate-400 default
  };

  // Fetch insights on mount
  useEffect(() => {
    fetchInsights();
  }, []);

  // Fetch insights from API
  const fetchInsights = async () => {
    try {
      setIsLoading(true);
      
      // Check authentication
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        router.push("/login");
        return;
      }
      
      // Fetch insights
      const { data: insightsData, error: insightsError } = await supabase
        .from("insights")
        .select("*")
        .eq("user_id", session.user.id)
        .order("created_at", { ascending: false });
        
      if (insightsError) throw insightsError;
      
      // Fetch user summary
      const { data: summaryData, error: summaryError } = await supabase
        .from("user_summaries")
        .select("*")
        .eq("user_id", session.user.id)
        .single();
      
      if (summaryError && summaryError.code !== "PGRST116") {
        console.error("Error fetching summary:", summaryError);
      }
      
      // Fetch graph data
      const { data: graphData, error: graphError } = await supabase
        .rpc("get_user_knowledge_graph", { user_id: session.user.id });
      
      if (graphError) {
        console.error("Error fetching graph data:", graphError);
      }
      
      // Set state
      setInsights(insightsData || []);
      
      if (summaryData) {
        setUserSummary(summaryData.summary);
      }
      
      if (graphData) {
        // Transform graph data
        const transformedData = transformGraphData(graphData);
        setGraphData(transformedData);
      } else {
        // Create sample graph data if none exists
        setGraphData(createSampleGraphData(insightsData || []));
      }
      
    } catch (error) {
      console.error("Error fetching insights:", error);
      toast({
        title: "Error",
        description: "Failed to load insights. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Transform graph data from API format to force-graph format
  const transformGraphData = (data: any): GraphData => {
    try {
      // Check if data already has nodes and links structure
      if (data.nodes && data.links) {
        return {
          nodes: data.nodes.map((node: any) => ({
            ...node,
            color: getNodeColor(node.type),
            size: node.type === "user" ? 15 : 8
          })),
          links: data.links
        };
      }
      
      // If not, create from scratch
      return createSampleGraphData(insights);
      
    } catch (error) {
      console.error("Error transforming graph data:", error);
      return createSampleGraphData(insights);
    }
  };

  // Create sample graph data from insights
  const createSampleGraphData = (insights: Insight[]): GraphData => {
    const nodes: GraphNode[] = [
      {
        id: "user",
        label: "You",
        type: "user",
        color: getNodeColor("user"),
        size: 15
      }
    ];
    
    const links: GraphLink[] = [];
    const addedNodes = new Set<string>(["user"]);
    
    // Create nodes and links from insights
    insights.forEach(insight => {
      const nodeId = insight.id;
      
      if (!addedNodes.has(nodeId)) {
        nodes.push({
          id: nodeId,
          label: insight.content.substring(0, 30) + "...",
          type: insight.type.toLowerCase(),
          content: insight.content,
          evidence: insight.evidence,
          color: getNodeColor(insight.type),
          size: 8
        });
        
        addedNodes.add(nodeId);
        
        // Create link to user
        links.push({
          source: "user",
          target: nodeId,
          label: `has_${insight.type.toLowerCase()}`
        });
      }
    });
    
    // Create some additional links between related insights
    // This is a simplified approach - in a real app, you'd determine relationships based on content similarity
    for (let i = 0; i < insights.length - 1; i++) {
      if (Math.random() > 0.7) { // Only create a connection ~30% of the time
        const sourceId = insights[i].id;
        const targetId = insights[i + 1].id;
        
        if (addedNodes.has(sourceId) && addedNodes.has(targetId)) {
          links.push({
            source: sourceId,
            target: targetId,
            label: "related_to"
          });
        }
      }
    }
    
    return { nodes, links };
  };

  // Filter insights by type
  const filterInsightsByType = (type: string | null) => {
    setSelectedInsightType(type);
    
    if (graphRef.current) {
      const graphInstance = graphRef.current;
      
      if (type) {
        // Highlight nodes of selected type
        graphInstance.nodeColor((node: GraphNode) => 
          node.type === type ? getNodeColor(type) : "#CBD5E1" // slate-300
        );
        
        // Dim links that don't connect to highlighted nodes
        graphInstance.linkColor((link: GraphLink) => {
          const sourceNode = typeof link.source === 'object' ? link.source : graphData.nodes.find(n => n.id === link.source);
          const targetNode = typeof link.target === 'object' ? link.target : graphData.nodes.find(n => n.id === link.target);
          
          if (sourceNode?.type === type || targetNode?.type === type) {
            return "#64748B"; // slate-500
          }
          return "#E2E8F0"; // slate-200
        });
      } else {
        // Reset colors
        graphInstance.nodeColor((node: GraphNode) => node.color);
        graphInstance.linkColor(() => "#94A3B8"); // slate-400
      }
    }
  };

  // Export insights as JSON
  const exportInsights = () => {
    try {
      const data = JSON.stringify(insights, null, 2);
      const blob = new Blob([data], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `insights-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Insights exported",
        description: "Your insights have been exported as JSON.",
      });
    } catch (error) {
      console.error("Error exporting insights:", error);
      toast({
        title: "Error",
        description: "Failed to export insights. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Get insight type counts
  const getInsightTypeCounts = () => {
    const counts: Record<string, number> = {};
    
    insights.forEach(insight => {
      const type = insight.type.toLowerCase();
      counts[type] = (counts[type] || 0) + 1;
    });
    
    return counts;
  };

  // Filter insights by selected type
  const filteredInsights = selectedInsightType
    ? insights.filter(insight => insight.type.toLowerCase() === selectedInsightType.toLowerCase())
    : insights;

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen pb-12">
      <div className="absolute inset-0 -z-10">
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={30}
          className="w-full h-full"
          particleColor="#FFFFFF"
        />
      </div>
      
      <MainNav />
      
      <div className="container max-w-7xl px-4 mx-auto mt-8">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Insights</h1>
            <p className="text-muted-foreground mt-1">
              Discoveries and patterns from your conversations
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={exportInsights}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </header>
        
        {insights.length === 0 ? (
          <Card className="py-16">
            <div className="text-center">
              <Lightbulb className="h-16 w-16 mx-auto mb-6 text-muted-foreground" />
              <h2 className="text-2xl font-bold mb-2">No insights yet</h2>
              <p className="text-muted-foreground max-w-xl mx-auto mb-8">
                Insights are automatically generated as you have more conversations with DeepIntrospect AI.
                Start chatting to begin building your personal insights.
              </p>
              <Button onClick={() => router.push("/chat")}>Start a conversation</Button>
            </div>
          </Card>
        ) : (
          <>
            {/* View Mode Tabs */}
            <Tabs value={viewMode} onValueChange={setViewMode} className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <TabsList>
                  <TabsTrigger value="list">
                    <Lightbulb className="h-4 w-4 mr-2" />
                    List View
                  </TabsTrigger>
                  <TabsTrigger value="graph">
                    <Network className="h-4 w-4 mr-2" />
                    Graph View
                  </TabsTrigger>
                  <TabsTrigger value="summary">
                    <BrainCircuit className="h-4 w-4 mr-2" />
                    Summary
                  </TabsTrigger>
                </TabsList>
                
                {viewMode === "list" && (
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-wrap gap-1">
                      <Badge 
                        variant={selectedInsightType === null ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => filterInsightsByType(null)}
                      >
                        All
                      </Badge>
                      {Object.entries(getInsightTypeCounts()).map(([type, count]) => (
                        <Badge 
                          key={type}
                          variant={selectedInsightType === type ? "default" : "outline"}
                          className="cursor-pointer"
                          onClick={() => filterInsightsByType(type)}
                        >
                          {type} ({count})
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {viewMode === "graph" && (
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-wrap gap-1">
                      <Badge 
                        variant={selectedInsightType === null ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => filterInsightsByType(null)}
                      >
                        All
                      </Badge>
                      {Object.entries(getInsightTypeCounts()).map(([type, count]) => (
                        <Badge 
                          key={type}
                          variant={selectedInsightType === type ? "default" : "outline"}
                          className="cursor-pointer"
                          onClick={() => filterInsightsByType(type)}
                        >
                          {type} ({count})
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              {/* List View */}
              <TabsContent value="list" className="space-y-6">
                {filteredInsights.map((insight) => (
                  <Card key={insight.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <Badge className="capitalize">
                          <TagIcon className="h-3 w-3 mr-1" />
                          {insight.type}
                        </Badge>
                        <div className="text-sm text-muted-foreground flex items-center">
                          <Calendar className="h-3 w-3 mr-1" />
                          {formatDate(insight.created_at)}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-lg font-medium mb-4">{insight.content}</p>
                      {insight.evidence && (
                        <div className="mt-2 bg-muted p-3 rounded-md text-sm italic">
                          "{insight.evidence}"
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>
              
              {/* Graph View */}
              <TabsContent value="graph">
                <Card>
                  <CardHeader>
                    <CardTitle>Knowledge Graph</CardTitle>
                    <CardDescription>
                      Visual representation of your insights and their connections
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[600px] bg-muted/50 rounded-md overflow-hidden">
                      {graphData.nodes.length > 0 ? (
                        <ForceGraph2D
                          ref={graphRef}
                          graphData={graphData}
                          nodeLabel={(node: any) => `${node.label} (${node.type})`}
                          nodeAutoColorBy="type"
                          nodeColor={(node: any) => node.color}
                          nodeVal={(node: any) => node.size}
                          linkLabel={(link: any) => link.label}
                          linkDirectionalArrowLength={3}
                          linkDirectionalArrowRelPos={1}
                          linkCurvature={0.25}
                          backgroundColor="rgba(0,0,0,0)"
                          onNodeClick={(node: any) => {
                            if (node.content) {
                              toast({
                                title: node.type,
                                description: node.content,
                              });
                            }
                          }}
                        />
                      ) : (
                        <div className="h-full flex items-center justify-center">
                          <p className="text-muted-foreground">No graph data available</p>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-4 flex flex-wrap gap-3">
                      <div className="text-sm text-muted-foreground">Node Types:</div>
                      {Object.entries(getInsightTypeCounts()).map(([type, count]) => (
                        <div key={type} className="flex items-center gap-1 text-sm">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: getNodeColor(type) }}
                          />
                          <span className="capitalize">{type}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              {/* Summary View */}
              <TabsContent value="summary">
                <Card>
                  <CardHeader>
                    <CardTitle>Personal Summary</CardTitle>
                    <CardDescription>
                      A comprehensive summary of insights about you
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {userSummary ? (
                      <>
                        <div>
                          <h3 className="text-lg font-medium mb-2">Overall Summary</h3>
                          <p>{userSummary.summary}</p>
                        </div>
                        
                        <Separator />
                        
                        <div>
                          <h3 className="text-lg font-medium mb-2">Key Traits</h3>
                          <p>{userSummary.categories.traits}</p>
                        </div>
                        
                        <Separator />
                        
                        <div>
                          <h3 className="text-lg font-medium mb-2">Values & Beliefs</h3>
                          <p>{userSummary.categories.values_beliefs}</p>
                        </div>
                        
                        <Separator />
                        
                        <div>
                          <h3 className="text-lg font-medium mb-2">Goals & Aspirations</h3>
                          <p>{userSummary.categories.goals_aspirations}</p>
                        </div>
                        
                        <Separator />
                        
                        <div>
                          <h3 className="text-lg font-medium mb-2">Challenges</h3>
                          <p>{userSummary.categories.challenges}</p>
                        </div>
                        
                        <Separator />
                        
                        <div>
                          <h3 className="text-lg font-medium mb-2">Patterns</h3>
                          <p>{userSummary.categories.patterns}</p>
                        </div>
                      </>
                    ) : (
                      <div className="py-8 text-center">
                        <BrainCircuit className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                        <h3 className="text-lg font-medium mb-2">No summary available yet</h3>
                        <p className="text-muted-foreground mb-6">
                          Your personal summary will be generated once you have enough conversations and insights.
                          Continue chatting with DeepIntrospect AI to build your profile.
                        </p>
                        <Button onClick={() => router.push("/chat")}>
                          Continue conversations
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </>
        )}
      </div>
    </div>
  );
}
