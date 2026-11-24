import { useState, useCallback, useRef, type DragEvent } from "react";
import { api } from "@/shared/api/client";
import styles from "./UploadZone.module.css";

interface Props {
  caseId: number;
  onUploaded: () => void;
}

export function UploadZone({ caseId, onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const uploadFiles = useCallback(
    async (files: FileList | File[]) => {
      setUploading(true);
      setMessage("");
      let ok = 0;
      let fail = 0;
      for (const file of Array.from(files)) {
        try {
          const form = new FormData();
          form.append("file", file);
          await api.post(`/documents/upload/${caseId}`, form);
          ok++;
        } catch {
          fail++;
        }
      }
      setUploading(false);
      if (fail > 0) {
        setMessage(`${ok} envoye(s), ${fail} echec(s)`);
      } else {
        setMessage(`${ok} document(s) envoye(s)`);
      }
      onUploaded();
    },
    [caseId, onUploaded],
  );

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
  };

  return (
    <div
      className={`${styles.zone} ${dragging ? styles.active : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif"
        className={styles.hidden}
        onChange={(e) => {
          if (e.target.files?.length) uploadFiles(e.target.files);
        }}
      />
      {uploading ? (
        <p className={styles.text}>Envoi en cours...</p>
      ) : (
        <>
          <p className={styles.text}>
            Glissez vos documents ici ou cliquez pour selectionner
          </p>
          <p className={styles.hint}>PDF, PNG, JPEG, TIFF — max 20 Mo</p>
        </>
      )}
      {message && <p className={styles.msg}>{message}</p>}
    </div>
  );
}
