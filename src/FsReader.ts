import { Filelike } from "@foxglove/rosbag2";
import { FileHandle, open as fopen, readFile } from "fs/promises";

export class FsReader implements Filelike {
  static DEFAULT_BUFFER_SIZE = 1024 * 16;

  readonly filename: string;
  private size_?: number;
  private handle_?: FileHandle;
  private buffer_: Uint8Array;

  constructor(filename: string) {
    this.filename = filename;
    this.buffer_ = new Uint8Array(FsReader.DEFAULT_BUFFER_SIZE);
  }

  async read(offset = 0, length = Math.max(0, (this.size_ ?? 0) - offset)): Promise<Uint8Array> {
    const handle = this.handle_ ?? (await this.open());

    if (length > this.buffer_.byteLength) {
      const newSize = Math.max(this.buffer_.byteLength * 2, length);
      this.buffer_ = new Uint8Array(newSize);
    }

    await handle.read(this.buffer_, 0, length, offset);
    return this.buffer_.byteLength === length
      ? this.buffer_
      : new Uint8Array(this.buffer_.buffer, 0, length);
  }

  async readAsText(): Promise<string> {
    return await readFile(this.filename, { encoding: "utf8" });
  }

  async size(): Promise<number> {
    if (this.size_ != undefined) {
      return this.size_;
    }
    await this.open();
    return this.size_ ?? 0;
  }

  async close(): Promise<void> {
    if (this.handle_ == undefined) {
      return;
    }

    await this.handle_.close();
    this.size_ = undefined;
    this.handle_ = undefined;
  }

  private async open(): Promise<FileHandle> {
    this.handle_ = await fopen(this.filename, "r");
    this.size_ = (await this.handle_.stat()).size;
    return this.handle_;
  }
}
