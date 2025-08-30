import * as React from "react";
import Plot from "react-plotly.js";
import * as Plotly from "plotly.js";
import {
  FuncNodesReactPlugin,
  LATEST_VERSION,
  RenderPluginFactoryProps,
  RendererPlugin,
  DataViewRendererType,
  DataViewRendererProps,
  DataViewRendererToDataPreviewViewRenderer,
} from "@linkdlab/funcnodes-react-flow-plugin";
import "./style.css";

// Minimum delay between renders in milliseconds
const RENDER_DELAY_MS = 1000;

const PreviewPlotlyImageRenderer: DataViewRendererType = ({
  value,
}: DataViewRendererProps) => {
  const [renderedValue, setRenderedValue] = React.useState(value);
  const latestValueRef = React.useRef(value);
  const timeoutRef = React.useRef<number | null>(null);
  const lastRenderTimeRef = React.useRef<number>(0);

  const scheduleRender = React.useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTimeRef.current;
    const delay = Math.max(0, RENDER_DELAY_MS - timeSinceLastRender);

    timeoutRef.current = setTimeout(() => {
      setRenderedValue(latestValueRef.current);
      lastRenderTimeRef.current = Date.now();
      timeoutRef.current = null;
    }, delay);
  }, []);

  React.useEffect(() => {
    latestValueRef.current = value;
    scheduleRender();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, scheduleRender]);

  if (!renderedValue) return <></>;
  // if not an object, return null
  if (typeof renderedValue !== "object") return <></>;
  if (!("data" in renderedValue) || !("layout" in renderedValue)) return <></>;

  const { data, layout, ...rest } = renderedValue;
  // if not an object, return null
  const plotlylayout = layout as unknown as Plotly.Layout;
  plotlylayout.autosize = true;
  return (
    <div className="funcnodes_plotly_container">
      <Plot
        data={data as unknown as Plotly.Data[]}
        layout={plotlylayout}
        config={{
          staticPlot: true, // no interactions
          displayModeBar: false, // no UI chrome
          responsive: true, // let it fit the container
          doubleClick: false,
          scrollZoom: false,
        }}
        useResizeHandler
        style={{
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
        {...rest}
      />
    </div>
  );
};

const PlotlyImageRenderer: DataViewRendererType = ({
  value,
}: DataViewRendererProps) => {
  const [renderedValue, setRenderedValue] = React.useState(value);
  const latestValueRef = React.useRef(value);
  const timeoutRef = React.useRef<number | null>(null);
  const lastRenderTimeRef = React.useRef<number>(0);

  const scheduleRender = React.useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTimeRef.current;
    const delay = Math.max(0, RENDER_DELAY_MS - timeSinceLastRender);

    timeoutRef.current = setTimeout(() => {
      setRenderedValue(latestValueRef.current);
      lastRenderTimeRef.current = Date.now();
      timeoutRef.current = null;
    }, delay);
  }, []);

  React.useEffect(() => {
    latestValueRef.current = value;
    scheduleRender();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, scheduleRender]);

  if (!renderedValue) return <></>;
  // if not an object, return null
  if (typeof renderedValue !== "object") return <></>;
  if (!("data" in renderedValue) || !("layout" in renderedValue)) return <></>;

  const { data, layout, ...rest } = renderedValue;
  // if not an object, return null
  const plotlylayout = layout as unknown as Plotly.Layout;
  plotlylayout.autosize = true;
  return (
    <Plot
      data={data as unknown as Plotly.Data[]}
      layout={plotlylayout}
      style={{
        width: "100%",
        height: "100%",
      }}
      useResizeHandler
      {...rest}
    />
  );
};

const renderpluginfactory = ({}: RenderPluginFactoryProps) => {
  const MyRendererPlugin: RendererPlugin = {
    // data_overlay_renderers: {
    //   "plotly.Figure": PlotlyOverlayRenderer,
    // },
    data_preview_renderers: {
      "plotly.Figure": DataViewRendererToDataPreviewViewRenderer(
        PreviewPlotlyImageRenderer
      ),
    },
    data_view_renderers: {
      "plotly.Figure": PlotlyImageRenderer,
    },
  };

  return MyRendererPlugin;
};

const Plugin: FuncNodesReactPlugin = {
  renderpluginfactory: renderpluginfactory,
  v: LATEST_VERSION,
};

export default Plugin;
