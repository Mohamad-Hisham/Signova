import type { InputLimits } from "../api/contracts";
import type { LiveSocket } from "../api/liveSocket";

type PendingAck = {
  streamId: string;
  frameSeq: number;
  resolve: (matched: boolean) => void;
  timer: number;
};

type EncodedFrame = {
  blob: Blob;
  captureMs: number;
  width: number;
  height: number;
};

export class FrameSampler {
  private generation = 0;
  private active = false;
  private frameSeq = 0;
  private pendingAck: PendingAck | null = null;
  private canvas = document.createElement("canvas");

  constructor(private readonly onFailure: (reason: string) => void) {}

  start(
    video: HTMLVideoElement,
    socket: LiveSocket,
    streamId: string,
    limits: InputLimits,
  ): void {
    this.stop();
    this.active = true;
    this.frameSeq = 0;
    const generation = this.generation;
    void this.sampleLoop(video, socket, streamId, limits, generation);
  }

  acknowledge(streamId: string, frameSeq: number): void {
    const pending = this.pendingAck;
    if (
      !pending ||
      pending.streamId !== streamId ||
      pending.frameSeq !== frameSeq
    ) {
      return;
    }
    window.clearTimeout(pending.timer);
    this.pendingAck = null;
    pending.resolve(true);
  }

  stop(): void {
    this.generation += 1;
    this.active = false;
    if (this.pendingAck) {
      window.clearTimeout(this.pendingAck.timer);
      this.pendingAck.resolve(false);
      this.pendingAck = null;
    }
  }

  private async sampleLoop(
    video: HTMLVideoElement,
    socket: LiveSocket,
    streamId: string,
    limits: InputLimits,
    generation: number,
  ): Promise<void> {
    const sampleFps = limits.required_sample_fps ?? limits.max_fps;
    if (sampleFps > limits.max_fps) {
      throw new Error("INVALID_REQUIRED_SAMPLE_RATE");
    }
    const intervalMs = 1000 / sampleFps;
    while (this.isCurrent(generation)) {
      const startedAt = performance.now();
      try {
        if (video.videoWidth < 1 || video.videoHeight < 1) {
          throw new Error("VIDEO_NOT_READY");
        }
        if (socket.readyState !== WebSocket.OPEN) {
          throw new Error("SOCKET_NOT_OPEN");
        }
        if (socket.bufferedAmount > 262_144) {
          throw new Error("SOCKET_BACKPRESSURE");
        }

        const encoded = await this.encode(video, limits);
        if (!this.isCurrent(generation)) return;
        if (encoded.blob.size > limits.max_jpeg_bytes) {
          throw new Error("FRAME_TOO_LARGE");
        }

        const imageB64 = await this.toBase64(encoded.blob);
        if (!this.isCurrent(generation)) return;

        const frameSeq = this.frameSeq + 1;
        const frame = {
          protocol_version: 1,
          type: "frame",
          stream_id: streamId,
          frame_seq: frameSeq,
          capture_ms: encoded.captureMs,
          width: encoded.width,
          height: encoded.height,
          mirrored: false,
          image_b64: imageB64,
        };
        if (
          new TextEncoder().encode(JSON.stringify(frame)).byteLength >
          limits.max_message_bytes
        ) {
          throw new Error("FRAME_MESSAGE_TOO_LARGE");
        }
        if (!this.isCurrent(generation)) return;

        this.frameSeq = frameSeq;
        socket.send(frame);
        const acknowledged = await this.waitForAck(streamId, frameSeq);
        if (!this.isCurrent(generation)) return;
        if (!acknowledged) throw new Error("FRAME_ACK_TIMEOUT");

        const remaining = intervalMs - (performance.now() - startedAt);
        if (remaining > 0) await this.delay(remaining, generation);
      } catch (cause) {
        if (this.isCurrent(generation)) {
          this.stop();
          this.onFailure(
            cause instanceof Error ? cause.message : "FRAME_SAMPLING_FAILED",
          );
        }
        return;
      }
    }
  }

  private async encode(
    video: HTMLVideoElement,
    limits: InputLimits,
  ): Promise<EncodedFrame> {
    const scale = Math.min(
      1,
      limits.max_width / video.videoWidth,
      limits.max_height / video.videoHeight,
    );
    let width = Math.max(1, Math.round(video.videoWidth * scale));
    let height = Math.max(1, Math.round(video.videoHeight * scale));
    const context = this.canvas.getContext("2d", { alpha: false });
    if (!context) throw new Error("CANVAS_UNAVAILABLE");

    for (let attempt = 0; attempt < 8; attempt += 1) {
      this.canvas.width = width;
      this.canvas.height = height;
      const captureMs = performance.now();
      context.drawImage(video, 0, 0, width, height);
      const quality = attempt < 3 ? [0.82, 0.7, 0.58][attempt] : 0.52;
      const blob = await new Promise<Blob>((resolve, reject) => {
        this.canvas.toBlob(
          result => {
            if (result) resolve(result);
            else reject(new Error("JPEG_ENCODING_FAILED"));
          },
          "image/jpeg",
          quality,
        );
      });
      if (blob.size <= limits.max_jpeg_bytes) {
        return { blob, captureMs, width, height };
      }
      width = Math.max(1, Math.floor(width * 0.86));
      height = Math.max(1, Math.floor(height * 0.86));
    }
    throw new Error("FRAME_TOO_LARGE");
  }

  private async toBase64(blob: Blob): Promise<string> {
    const bytes = new Uint8Array(await blob.arrayBuffer());
    let binary = "";
    const chunkSize = 0x8000;
    for (let offset = 0; offset < bytes.length; offset += chunkSize) {
      binary += String.fromCharCode(...bytes.subarray(offset, offset + chunkSize));
    }
    return btoa(binary);
  }

  private waitForAck(streamId: string, frameSeq: number): Promise<boolean> {
    return new Promise(resolve => {
      const timer = window.setTimeout(() => {
        if (
          this.pendingAck?.streamId === streamId &&
          this.pendingAck.frameSeq === frameSeq
        ) {
          this.pendingAck = null;
          resolve(false);
        }
      }, 3000);
      this.pendingAck = { streamId, frameSeq, resolve, timer };
    });
  }

  private delay(duration: number, generation: number): Promise<void> {
    return new Promise(resolve => {
      const timer = window.setTimeout(resolve, duration);
      if (!this.isCurrent(generation)) {
        window.clearTimeout(timer);
        resolve();
      }
    });
  }

  private isCurrent(generation: number): boolean {
    return this.active && this.generation === generation;
  }
}
