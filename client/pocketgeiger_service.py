#!/usr/bin/env python3
import serial
import threading
import os
import json
import time
from collections import deque
from statistics import mean

class PocketGeigerService:
    def __init__(self, device='/dev/ttyPG', baudrate=38400, 
                 output_file='/var/lib/pocketgeiger/data.json'):
        self.device = device
        self.baudrate = baudrate
        self.output_file = output_file
        self.running = False
        
        # データ保存用 (最大30秒分 = 300サンプル)
        self.signal_data = deque(maxlen=300)
        self.noise_data = deque(maxlen=300)
        self.lock = threading.Lock()
        
        # データ収集開始時刻
        self.start_time = None
        
        self.serial_conn = None
        
        # 出力ディレクトリ作成
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
    def start(self):
        """サービス開始"""
        self.running = True
        self.start_time = time.time()
        
        # シリアル接続
        self.serial_conn = serial.Serial(self.device, self.baudrate, timeout=1)
        time.sleep(0.5)
        
        # 測定開始コマンド送信
        self.serial_conn.write(b'S')
        response = self.serial_conn.readline().decode().strip()
        print(f"Start response: {response}")
        
        # スレッド起動
        threading.Thread(target=self._serial_reader, daemon=True).start()
        threading.Thread(target=self._file_updater, daemon=True).start()
        
    def stop(self):
        """サービス停止"""
        self.running = False
        
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(b'E')
            response = self.serial_conn.readline().decode().strip()
            print(f"Stop response: {response}")
            self.serial_conn.close()
    
    def _serial_reader(self):
        """シリアルデータ読み取りスレッド"""
        while self.running:
            try:
                line = self.serial_conn.readline().decode().strip()
                
                if line.startswith('>'):
                    parts = line[1:].split(',')
                    if len(parts) == 2:
                        signal = int(parts[0])
                        noise = int(parts[1])
                        
                        with self.lock:
                            self.signal_data.append(signal)
                            self.noise_data.append(noise)
                            
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(0.1)
    
    def _calculate_averages(self):
        """各時間帯の平均値を計算"""
        with self.lock:
            if not self.signal_data:
                return None
            
            # 実際のデータ収集期間（秒）
            elapsed = time.time() - self.start_time
            actual_samples = len(self.signal_data)
            data_duration = min(elapsed, 30.0)  # 最大30秒
            
            result = {
                'timestamp': int(time.time()),
                'samples': actual_samples,
                'duration_sec': round(data_duration, 1),  # 実際のデータ期間
                'uptime_sec': round(elapsed, 1)  # サービス起動からの経過時間
            }
            
            # 1秒平均 (最新10サンプル)
            if len(self.signal_data) >= 10:
                result['signal_1s'] = round(mean(list(self.signal_data)[-10:]), 4)
                result['noise_1s'] = round(mean(list(self.noise_data)[-10:]), 4)
            else:
                result['signal_1s'] = None
                result['noise_1s'] = None
            
            # 3秒平均 (最新30サンプル)
            if len(self.signal_data) >= 30:
                result['signal_3s'] = round(mean(list(self.signal_data)[-30:]), 4)
                result['noise_3s'] = round(mean(list(self.noise_data)[-30:]), 4)
            else:
                result['signal_3s'] = None
                result['noise_3s'] = None
            
            # 10秒平均 (最新100サンプル)
            if len(self.signal_data) >= 100:
                result['signal_10s'] = round(mean(list(self.signal_data)[-100:]), 4)
                result['noise_10s'] = round(mean(list(self.noise_data)[-100:]), 4)
            else:
                result['signal_10s'] = None
                result['noise_10s'] = None
            
            # 30秒平均 (最新300サンプル)
            if len(self.signal_data) >= 300:
                result['signal_30s'] = round(mean(list(self.signal_data)[-300:]), 4)
                result['noise_30s'] = round(mean(list(self.noise_data)[-300:]), 4)
            else:
                result['signal_30s'] = None
                result['noise_30s'] = None
            
            return result
    
    def _file_updater(self):
        """定期的にファイルを更新"""
        while self.running:
            try:
                averages = self._calculate_averages()
                
                if averages:
                    # アトミックな書き込み（一時ファイル→rename）
                    temp_file = self.output_file + '.tmp'
                    with open(temp_file, 'w') as f:
                        json.dump(averages, f)
                        f.write('\n')
                    os.rename(temp_file, self.output_file)
                    os.chmod(self.output_file, 0o644)
                
                time.sleep(1)  # 1秒ごとに更新
                
            except Exception as e:
                print(f"File write error: {e}")
                time.sleep(1)

if __name__ == '__main__':
    import signal
    import sys
    
    service = PocketGeigerService()
    
    def signal_handler(sig, frame):
        print("\nShutting down...")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting Pocket Geiger Service...")
    service.start()
    
    while True:
        time.sleep(1)
