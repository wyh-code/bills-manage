import { useState, useEffect, useRef } from 'react';
import { fileApi } from '@/api/upload';

interface UseFileProgressParams {
  workspaceId: string;
  fileId?: string;
  onCompleted?: (bills: any[]) => void;
  onFailed?: () => void;
  pollingInterval?: number; // 轮询间隔（毫秒）
}

interface FileProgressState {
  status: 'idle' | 'processing' | 'completed' | 'failed';
  bills: any[];
  billsCount: number;
  isProcessing: boolean;
}

type UseFileProgressReturn = [
  state: FileProgressState,
  initStore: () => void
];

export const useFileProgress = ({
  workspaceId,
  fileId,
  onCompleted,
  onFailed,
  pollingInterval = 4000,
}: UseFileProgressParams): UseFileProgressReturn => {
  const defaultState: FileProgressState = {
    status: 'idle',
    bills: [],
    billsCount: 0,
    isProcessing: false,
  }
  const [state, setState] = useState<FileProgressState>(defaultState);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // 清理定时器
  const clearTimer = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  // 获取文件处理进度
  const fetchProgress = async () => {
    if (!workspaceId || !fileId) {
      return;
    }

    try {
      const result = await fileApi.getProgress(fileId, workspaceId);
      console.log('result: ', result)
      if (!isMountedRef.current) return;

      const { file_status, bills = [], bills_count } = result;

      setState({
        status: file_status,
        bills: bills || [],
        billsCount: bills_count || 0,
        isProcessing: file_status === 'processing',
      });

      // 根据状态决定是否继续轮询
      if (file_status === 'processing') {
        // 继续轮询
        timerRef.current = setTimeout(fetchProgress, pollingInterval);
      } else if (file_status === 'completed') {
        // 完成，调用回调
        clearTimer();
        onCompleted?.(bills || []);
      } else if (file_status === 'failed') {
        // 失败，调用回调
        clearTimer();
        onFailed?.();
      }
    } catch (error) {
      console.error('获取文件进度失败:', error);
      if (isMountedRef.current) {
        clearTimer();
        setState(prev => ({ ...prev, status: 'failed', isProcessing: false }));
        onFailed?.();
      }
    }
  };

  // 当 fileId 变化时开始轮询
  useEffect(() => {
    if (fileId && workspaceId) {
      setState(prev => ({ ...prev, status: 'processing', isProcessing: true }));
      fetchProgress();
    }

    return () => {
      clearTimer();
    };
  }, [fileId, workspaceId]);

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      clearTimer();
    };
  }, []);

  const initStore = () => setState(defaultState);

  return [state, initStore];
};