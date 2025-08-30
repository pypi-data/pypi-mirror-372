import * as React from "react";
import {
  FuncNodesReactPlugin,
  LATEST_VERSION,
  NodeHooksType,
  RenderPluginFactoryProps,
  RendererPlugin,
  NodeHooksProps,
  useIOStore,
  useSetIOValueOptions,
  useIOValueStore,
  InputRendererProps,
  OutputRendererProps,
  useWorkerApi,
  useSetIOValue,
  useFuncNodesContext,
  useIOGetFullValue,
  ArrayBufferDataStructure,
} from "@linkdlab/funcnodes-react-flow-plugin";

type FileDownloadProps = {
  filename: string;
  content: string;
};

const renderpluginfactory = ({}: RenderPluginFactoryProps) => {
  const FileInput = ({}: InputRendererProps) => {
    const fileInput = React.useRef<HTMLInputElement>(null);
    const iostore = useIOStore();
    const io_parent_store = useIOStore("parent");
    const node_id = iostore.use((s) => s.node);
    const connected = iostore.use((s) => s.connected);
    const set_io_value = useSetIOValue();
    const { worker } = useWorkerApi();
    const fnrf = useFuncNodesContext();
    const setProgress = (
      p: number,
      total: number | undefined,
      start: number
    ) => {
      fnrf.on_node_action({
        type: "update",
        id: node_id,
        node: {
          progress: {
            prefix: "Uploading",
            n: p,
            total: total,
            elapsed: (new Date().getTime() - start) / 1000,
            unit_scale: true,
            unit: "B",
            unit_divisor: 1024,
          },
        },
        from_remote: true,
      });
    };

    const on_change = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (!files || files.length === 0) return;
      if (!io_parent_store) return;
      const parent_io = io_parent_store.getState();
      let parentpath: string | undefined = undefined;
      for (let i = 0; i < 10; i++) {
        try {
          const full = io_parent_store.valuestore.getState().full;
          if (full) {
            parentpath = (full.value as any)?.["path"]?.toString();
            break;
          }
        } catch (e) {}
        if (parent_io.try_get_full_value === undefined) {
          break;
        }
        parent_io.try_get_full_value();
        await new Promise((resolve) => setTimeout(resolve, 500));
      }

      const start = new Date().getTime();

      const resp: string | undefined = await worker?.upload_file({
        files: files,
        onProgressCallback: (loaded: number, total?: number) => {
          setProgress(loaded, total, start);
        },
        root: parentpath,
      });

      set_io_value(resp, true);
    };

    return (
      <div>
        <input
          className="nodedatainput styledinput"
          type="file"
          // value={v}
          onChange={on_change}
          disabled={connected}
          style={{ display: "none" }}
          ref={fileInput}
        />
        <button
          className="nodedatainput styledinput"
          disabled={connected}
          onClick={() => {
            fileInput.current?.click();
          }}
        >
          Upload File
        </button>
      </div>
    );
  };

  const FolderInput = ({}: InputRendererProps) => {
    const fileInput = React.useRef<HTMLInputElement>(null);
    const iostore = useIOStore();
    const io_parent_store = useIOStore("parent");
    const node_id = iostore.use((s) => s.node);
    const connected = iostore.use((s) => s.connected);
    const { worker } = useWorkerApi();
    const fnrf = useFuncNodesContext();

    const set_io_value = useSetIOValue();
    const setProgress = (
      p: number,
      total: number | undefined,
      start: number
    ) => {
      fnrf.on_node_action({
        type: "update",
        id: node_id,
        node: {
          progress: {
            prefix: "Uploading",
            n: p,
            total: total,
            elapsed: (new Date().getTime() - start) / 1000,
            unit_scale: true,
            unit: "B",
            unit_divisor: 1024,
          },
        },
        from_remote: true,
      });
    };
    const on_change = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (!files || files.length === 0) return;
      if (!io_parent_store) return;

      let parentpath = undefined;
      const parentio = io_parent_store.getState();
      for (let i = 0; i < 10; i++) {
        try {
          const full = io_parent_store.valuestore.getState().full;
          if (full) {
            parentpath = (full.value as any)?.["path"]?.toString();
            break;
          }
        } catch (e) {}
        if (parentio.try_get_full_value === undefined) {
          break;
        }
        parentio.try_get_full_value();
        await new Promise((resolve) => setTimeout(resolve, 500));
      }

      const start = new Date().getTime();

      const resp: string | undefined = await worker?.upload_file({
        files: files,
        onProgressCallback: (loaded: number, total?: number) => {
          setProgress(loaded, total, start);
        },
        root: parentpath,
      });
      set_io_value(resp, true);
    };
    return (
      <div>
        <input
          className="nodedatainput styledinput"
          type="file"
          onChange={on_change}
          disabled={connected}
          style={{ display: "none" }}
          ref={fileInput}
          /* @ts-expect-error */
          webkitdirectory="true"
          directory="true"
          multiple
        />
        <button
          className="nodedatainput styledinput"
          disabled={connected}
          onClick={() => {
            fileInput.current?.click();
          }}
        >
          Upload Folder
        </button>
      </div>
    );
  };

  const FileDownload = ({}: OutputRendererProps) => {
    const fileDownload = React.useRef<HTMLAnchorElement>(null);
    const get_full_value = useIOGetFullValue();
    const filename = useIOValueStore("filename");
    console.log(filename);
    const download = React.useCallback(async () => {
      if (!get_full_value) return;
      if (!filename) return;
      const filenamestring = filename.preview?.toString() ?? "";
      if (!filenamestring) return;
      const fullvalue = (await get_full_value()) as
        | ArrayBufferDataStructure
        | undefined;
      if (!fullvalue) return;

      const a = fileDownload.current;
      a?.setAttribute("href", fullvalue.objectUrl);
      a?.setAttribute("download", filenamestring);
      a?.click();
    }, [get_full_value, filename]);

    return (
      <div>
        <a
          ref={fileDownload}
          style={{ display: "none" }}
          href=""
          download=""
        ></a>

        <button className="nodedatainput styledinput" onClick={download}>
          Download File
        </button>
      </div>
    );
  };

  const MyRendererPlugin: RendererPlugin = {
    input_renderers: {
      "funcnodes_files.FileUpload": FileInput,
      "funcnodes_files.FolderUpload": FolderInput,
    },
    output_renderers: {
      "funcnodes_files.FileDownload": FileDownload,
    },
  };

  return MyRendererPlugin;
};

const Plugin: FuncNodesReactPlugin = {
  renderpluginfactory: renderpluginfactory,
  v: LATEST_VERSION,
};

export default Plugin;
