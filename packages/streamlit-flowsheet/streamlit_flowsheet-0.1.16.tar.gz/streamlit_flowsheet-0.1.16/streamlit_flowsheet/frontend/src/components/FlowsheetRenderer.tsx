import React, { useState, useCallback, useMemo, useEffect } from 'react';
import ReactFlow, {
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  BackgroundVariant,
  Panel,
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import './FlowsheetRenderer.css';
import { PanelLeft, PanelLeftClose } from 'lucide-react';
import CustomNode from './CustomNode';
import NodeDetailsPanel from './NodeDetailsPanel';
import NodeHierarchy from './NodeHierarchy';
import type { FlowsheetData, SimulatorObjectNode } from '../types/flowsheet';

interface FlowsheetRendererProps {
  data?: FlowsheetData;
  showNavigationPanel?: boolean;
  showProperties?: boolean;
  showBorder?: boolean;
  theme?: any;
  onSelectionChange?: (selection: any[]) => void;
}

const nodeTypes = {
  custom: CustomNode,
};

const FlowsheetRendererInner: React.FC<FlowsheetRendererProps> = ({
  data,
  showNavigationPanel = true,
  showProperties = true,
  showBorder = true,
  theme = {},
  onSelectionChange
}) => {
  const [currentData] = useState<FlowsheetData | null>(data || null);
  const [selectedNode, setSelectedNode] = useState<{ id: string; label: string; type: string; properties?: any[] } | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [isHierarchyOpen, setIsHierarchyOpen] = useState(showNavigationPanel);

  const handleNodeClick = useCallback((nodeData: { id: string; label: string; type: string; properties?: any[] }) => {
    setSelectedNode(nodeData);
    if (showProperties) {
      setIsPanelOpen(true);
    }

    if (onSelectionChange) {
      const nodes = currentData?.simulatorObjectNodes;
      if (nodes) {
        const selectedNodeFull = nodes.find(n => n.id === nodeData.id);
        if (selectedNodeFull) {
          onSelectionChange([{
            id: selectedNodeFull.id,
            name: selectedNodeFull.name,
            type: selectedNodeFull.type,
            properties: selectedNodeFull.properties || []
          }]);
        }
      }
    }
  }, [showProperties, onSelectionChange, currentData]);

  const handlePanelClose = useCallback(() => {
    setIsPanelOpen(false);
    setSelectedNode(null);
    if (onSelectionChange) {
      onSelectionChange([]);
    }
  }, [onSelectionChange]);

  const handlePaneClick = useCallback(() => {
    setIsPanelOpen(false);
    setSelectedNode(null);
    if (onSelectionChange) {
      onSelectionChange([]);
    }
  }, [onSelectionChange]);

  const handleHierarchyNodeSelect = useCallback((node: SimulatorObjectNode) => {
    const nodeData = {
      id: node.id,
      label: node.name,
      type: node.type,
      properties: node.properties,
    };
    handleNodeClick(nodeData);

    if (reactFlowInstance.current) {
      const nodeElement = reactFlowInstance.current.getNode(node.id);
      if (nodeElement) {
        reactFlowInstance.current.fitView({
          padding: 8.0,
          duration: 800,
          nodes: [nodeElement],
        });
      }
    }
  }, [handleNodeClick]);

  const handleNodeDragStart = useCallback((_event: React.MouseEvent, node: Node) => {
    // Trigger node selection when drag starts
    const nodeData = {
      id: node.id,
      label: node.data.label,
      type: node.data.type,
      properties: node.data.properties,
    };
    handleNodeClick(nodeData);
  }, [handleNodeClick]);

  const reactFlowInstance = React.useRef<any>(null);

  const { nodes: reactFlowNodes, edges: reactFlowEdges } = useMemo(() => {
    if (!currentData) {
      return { nodes: [], edges: [] };
    }

    // Handle missing or empty simulatorObjectNodes
    if (!currentData.simulatorObjectNodes || currentData.simulatorObjectNodes.length === 0) {
      return { nodes: [], edges: [] };
    }

    // Calculate smart scaling based on edge distances
    const calculateSmartScale = () => {
      const nodes = currentData.simulatorObjectNodes;
      if (!nodes || nodes.length === 0) {
        return 2.5;
      }

      // Get all edges with valid source and target positions
      const edgesWithPositions = (currentData.simulatorObjectEdges || []).map((edge: any) => {
        const sourceNode = nodes.find((n: SimulatorObjectNode) => n.id === edge.sourceId);
        const targetNode = nodes.find((n: SimulatorObjectNode) => n.id === edge.targetId);

        if (sourceNode?.graphicalObject?.position && targetNode?.graphicalObject?.position) {
          const dx = targetNode.graphicalObject.position.x - sourceNode.graphicalObject.position.x;
          const dy = targetNode.graphicalObject.position.y - sourceNode.graphicalObject.position.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          return { edge, distance, sourceNode, targetNode };
        }
        return null;
      }).filter((e): e is NonNullable<typeof e> => e !== null);

      if (edgesWithPositions.length === 0) {
        return 2.5; // Default scale if no edges
      }

      // Find minimum edge distance
      const minEdgeDistance = Math.min(...edgesWithPositions.map(e => e.distance));

      // Estimate rendered node height: padding (20px) + icon (40px) + margin (8px) + text (~20px)
      const estimatedNodeHeight = 88;

      // Calculate scale so that minimum edge length is at least 1.2x the estimated node height
      const desiredMinEdgeLength = estimatedNodeHeight * 1.2;
      let scale = 1;

      if (minEdgeDistance > 0) {
        scale = desiredMinEdgeLength / minEdgeDistance;
        // Clamp scale to reasonable bounds
        scale = Math.max(0.5, Math.min(5, scale));
      }

      return scale;
    };

    const POSITION_SCALE = calculateSmartScale();

    const nodes: Node[] = currentData.simulatorObjectNodes.map((node: SimulatorObjectNode) => {
      const originalPos = node.graphicalObject?.position || { x: 0, y: 0 };
      return {
        id: node.id,
        type: 'custom',
        position: { 
          x: originalPos.x * POSITION_SCALE, 
          y: originalPos.y * POSITION_SCALE 
        },
        data: {
          label: node.name,
          type: node.type,
          properties: node.properties,
          showBox: showBorder,
          onNodeClick: handleNodeClick,
          theme: theme,
        },
        selected: selectedNode?.id === node.id,
      };
    });

    // Handle missing or empty simulatorObjectEdges
    const edgesArray = currentData.simulatorObjectEdges || [];
    const edges: Edge[] = edgesArray.map((edge: any) => {
      return {
        id: edge.id,
        source: edge.sourceId,
        target: edge.targetId,
        type: 'straight', // Straight lines connecting node centers
        animated: false,
        style: {
          stroke: theme.textColor || '#6b7280',
          strokeWidth: 2,
        },
      };
    });

    return { nodes, edges };
  }, [currentData, selectedNode, handleNodeClick, showBorder, theme]);

  const [nodes, setNodes, onNodesChange] = useNodesState(reactFlowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(reactFlowEdges);

  useEffect(() => {
    setNodes(reactFlowNodes);
    setEdges(reactFlowEdges);
  }, [reactFlowNodes, reactFlowEdges, setNodes, setEdges]);

  const onInit = useCallback((instance: any) => {
    reactFlowInstance.current = instance;
    setTimeout(() => {
      instance.fitView({ padding: 0.1 });
    }, 100);
  }, []);

  // Detect dark mode based on background color
  const isDarkMode = useMemo(() => {
    const bgColor = theme.backgroundColor || '#fff';
    // Simple heuristic: if background is dark (low luminance), we're in dark mode
    return bgColor.toLowerCase().includes('dark') || 
           bgColor === '#1f2937' || 
           bgColor === '#111827' ||
           bgColor === '#000' ||
           bgColor === '#000000' ||
           (bgColor.startsWith('#') && parseInt(bgColor.slice(1, 3), 16) < 128);
  }, [theme.backgroundColor]);

  const containerStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    display: 'flex',
    position: 'relative',
    backgroundColor: theme.backgroundColor || '#fff',
  };

  const hierarchyContainerStyle: React.CSSProperties = {
    width: isHierarchyOpen ? '250px' : '0',
    borderRight: isHierarchyOpen ? `1px solid ${theme.borderColor || '#e5e7eb'}` : 'none',
    transition: 'width 0.3s ease',
    overflow: 'hidden',
    backgroundColor: theme.secondaryBackgroundColor || '#f9fafb',
  };

  const flowContainerStyle: React.CSSProperties = {
    flex: 1,
    position: 'relative',
  };

  const toggleButtonStyle: React.CSSProperties = {
    background: theme.backgroundColor || '#fff',
    border: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    borderRadius: '6px',
    padding: '8px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s',
  };

  return (
    <div style={containerStyle} data-theme={isDarkMode ? 'dark' : 'light'}>
      {showNavigationPanel && (
        <div style={hierarchyContainerStyle}>
          {currentData && isHierarchyOpen && currentData.simulatorObjectNodes && (
            <NodeHierarchy
              nodes={currentData.simulatorObjectNodes}
              selectedNodeId={selectedNode?.id}
              onNodeSelect={handleHierarchyNodeSelect}
              theme={theme}
            />
          )}
        </div>
      )}

      <div style={flowContainerStyle}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onInit={onInit}
          onPaneClick={handlePaneClick}
          onNodeDragStart={handleNodeDragStart}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.05}
          maxZoom={4}
          style={{ backgroundColor: theme.backgroundColor || '#fff' }}
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={12}
            size={1}
            color={theme.dotColor || '#e5e7eb'}
          />
          <Controls 
            style={{
              backgroundColor: theme.backgroundColor || '#fff',
              border: `1px solid ${theme.borderColor || '#e5e7eb'}`,
              borderRadius: '8px',
            }}
          />
          <MiniMap
            nodeColor={(node) => {
              // Use theme primary color for all nodes, with higher opacity for selected
              const baseColor = theme.primaryColor || '#0ea5e9';
              return node.selected ? baseColor : `${baseColor}99`; // Add transparency for non-selected
            }}
            nodeStrokeColor={(node) => {
              // Use theme primary color for stroke on selected nodes
              return node.selected ? (theme.primaryColor || '#0ea5e9') : 'transparent';
            }}
            nodeStrokeWidth={2}
            style={{
              backgroundColor: theme.backgroundColor || '#fff',
              border: `1px solid ${theme.borderColor || '#e5e7eb'}`,
            }}
          />

          {showNavigationPanel && (
            <Panel position="top-left">
              <button
                style={toggleButtonStyle}
                onClick={() => setIsHierarchyOpen(!isHierarchyOpen)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = theme.hoverBackgroundColor || '#f3f4f6';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = theme.backgroundColor || '#fff';
                }}
              >
                {isHierarchyOpen ? (
                  <PanelLeftClose size={18} color={theme.textColor || '#000'} />
                ) : (
                  <PanelLeft size={18} color={theme.textColor || '#000'} />
                )}
              </button>
            </Panel>
          )}
        </ReactFlow>

        {showProperties && isPanelOpen && selectedNode && (
          <NodeDetailsPanel
            node={selectedNode}
            onClose={handlePanelClose}
            theme={theme}
          />
        )}
      </div>
    </div>
  );
};

const FlowsheetRenderer: React.FC<FlowsheetRendererProps> = (props) => {
  return (
    <ReactFlowProvider>
      <FlowsheetRendererInner {...props} />
    </ReactFlowProvider>
  );
};

export default FlowsheetRenderer;