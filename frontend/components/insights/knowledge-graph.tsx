"use client"

import React, { useEffect, useRef, useState } from 'react';
import { ForceGraph3D } from 'react-force-graph';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  size?: number;
  content?: string;
  evidence?: string;
}

interface GraphLink {
  source: string;
  target: string;
  label: string;
  type?: string;
}

interface KnowledgeGraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface KnowledgeGraphProps {
  data?: KnowledgeGraphData;
  isLoading?: boolean;
  width?: number;
  height?: number;
}

export function KnowledgeGraph({
  data,
  isLoading = false,
  width = 800,
  height = 600
}: KnowledgeGraphProps) {
  const graphRef = useRef<any>();
  const [processedData, setProcessedData] = useState<any>({ nodes: [], links: [] });
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    if (data?.nodes && data?.links) {
      // Process data for visualization
      const nodes = data.nodes.map(node => ({
        ...node,
        color: getNodeColor(node.type),
        val: node.size || 1,
      }));

      const links = data.links.map(link => ({
        ...link,
        // Make sure source and target are strings matching node IDs
        source: typeof link.source === 'string' ? link.source : link.source.id,
        target: typeof link.target === 'string' ? link.target : link.target.id,
        color: getLinkColor(link.type || ''),
      }));

      setProcessedData({ nodes, links });
    }
  }, [data]);

  // Color mapping for different node types
  const getNodeColor = (type: string): string => {
    const typeColors: Record<string, string> = {
      user: '#ff7e5f',
      entity: '#0077b6',
      concept: '#8338ec',
      belief: '#219ebc',
      value: '#fb8500',
      pattern: '#ff006e',
      trait: '#3a86ff',
      default: '#cccccc',
    };

    return typeColors[type.toLowerCase()] || typeColors.default;
  };

  // Color mapping for different link types
  const getLinkColor = (type: string): string => {
    const typeColors: Record<string, string> = {
      relationship: '#aaaaaa',
      has_belief: '#219ebc',
      has_pattern: '#ff006e',
      has_value: '#fb8500',
      knows_about: '#0077b6',
      has_trait: '#3a86ff',
      default: '#aaaaaa',
    };

    return typeColors[type.toLowerCase()] || typeColors.default;
  };

  if (isLoading) {
    return (
      <Card className="w-full h-full flex items-center justify-center">
        <CardContent className="py-6">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="h-8 w-8 animate-spin" />
            <p className="text-muted-foreground">Loading knowledge graph...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <Card className="w-full h-full flex items-center justify-center">
        <CardContent className="py-6 text-center">
          <p className="text-muted-foreground">No knowledge graph data available yet.</p>
          <p className="text-muted-foreground text-sm mt-2">
            Continue chatting to build your personal knowledge graph.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="relative" style={{ width, height }}>
      <ForceGraph3D
        ref={graphRef}
        graphData={processedData}
        nodeLabel={(node: any) => node.label || node.id}
        linkLabel={(link: any) => link.label || ''}
        nodeColor={(node: any) => node.color}
        linkColor={(link: any) => link.color}
        nodeVal={(node: any) => node.val || 1}
        linkWidth={1}
        backgroundColor="rgba(0,0,0,0)"
        width={width}
        height={height}
        onNodeHover={(node: any) => {
          if (node) {
            setHoveredNode({
              id: node.id,
              label: node.label || node.id,
              type: node.type,
              content: node.content,
              evidence: node.evidence
            });
          } else {
            setHoveredNode(null);
          }
        }}
        onNodeClick={(node: any) => {
          if (graphRef.current) {
            const distance = 40;
            const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
            graphRef.current.cameraPosition(
              { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
              node,
              1000
            );
          }
        }}
      />
      
      {hoveredNode && (
        <div className="absolute bottom-4 left-4 bg-card p-3 rounded-md shadow-lg border border-border max-w-xs">
          <div className="font-medium">{hoveredNode.label}</div>
          <div className="text-xs text-muted-foreground uppercase mb-1">{hoveredNode.type}</div>
          {hoveredNode.content && (
            <div className="text-sm mt-1">{hoveredNode.content}</div>
          )}
          {hoveredNode.evidence && (
            <div className="text-xs text-muted-foreground mt-1 italic">
              Evidence: {hoveredNode.evidence}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
