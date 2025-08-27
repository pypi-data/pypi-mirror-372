# -*- coding: utf-8 -*-
"""
通用加密解密管理器模块

功能特性:
- RSA-OAEP + AES-GCM 混合加密
- dpflask风格设备指纹验证
- 时间窗口验证
- PEM格式密钥处理
- Redis防重放攻击（可选）

使用场景:
- 敏感数据传输加密
- 用户认证系统
- API安全通信
- 设备身份验证

依赖说明:
- cryptography: RSA和AES加密算法
- hashlib: 哈希计算（Python标准库）
- json: JSON处理（Python标准库）
- base64: Base64编码（Python标准库）
- redis: 防重放攻击（可选）
"""

import os
import json
import base64
import time
import hashlib
import hmac
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Union, List, Protocol, runtime_checkable

# 加密相关导入
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from mdbq.myconf import myconf # type: ignore
from mdbq.log import mylogger

dir_path = os.path.expanduser("~")
config_file = os.path.join(dir_path, 'spd.txt')
parser = myconf.ConfigParser()
logger = mylogger.MyLogger(
    logging_mode='file',
    log_level='info',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,  # 是否启用异步日志
    sample_rate=1,  # 采样DEBUG/INFO日志
    sensitive_fields=[],  #  敏感字段过滤
    enable_metrics=False,  # 是否启用性能指标
)


# ==================== 枚举和常量定义 ====================

class ValidationResult(Enum):
    """验证结果枚举"""
    SUCCESS = "success"
    DECRYPT_FAILED = "decrypt_failed"
    TIMESTAMP_INVALID = "timestamp_invalid" 
    FINGERPRINT_MISMATCH = "fingerprint_mismatch"
    NONCE_REUSED = "nonce_reused"
    INVALID_PAYLOAD = "invalid_payload"
    KEY_LOAD_FAILED = "key_load_failed"
    REDIS_ERROR = "redis_error"

# ==================== 配置类 ====================

@dataclass
class CryptoConfig:
    """加密配置类"""
    # 密钥配置
    key_dir_path: str = field(default_factory=lambda: os.path.expanduser("~"))
    public_key_filename: str = 'public_key'  # 公钥文件名
    private_key_filename: str = 'private_key'  # 私钥文件名
    keys_subdir: str = 'dpsk_keys'  # 密钥文件夹名
    
    # 验证配置
    time_window_seconds: int = 300  # 时间窗口，300秒
    enable_nonce_check: bool = True  # 是否启用nonce防重放攻击
    nonce_expire_seconds: int = 600  # 600秒后过期
    nonce_redis_prefix: str = "api_identity_check"  # 存储的键名
    
    # 缓存配置
    enable_key_cache: bool = True  # 是否启用密钥缓存
    key_cache_ttl_seconds: int = 3600  # 密钥缓存过期时间
    
    def __post_init__(self):
        """配置验证"""
        if self.time_window_seconds <= 0:
            raise ValueError("time_window_seconds must be positive")
        if self.nonce_expire_seconds <= 0:
            raise ValueError("nonce_expire_seconds must be positive")


# ==================== 结果类 ====================

@dataclass
class AuthResult:
    """认证结果类"""
    success: bool
    result_code: ValidationResult
    payload: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    execution_time_ms: Optional[float] = None
    debug_info: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, payload: Dict[str, Any], execution_time_ms: float = None) -> 'AuthResult':
        """创建成功结果"""
        return cls(
            success=True,
            result_code=ValidationResult.SUCCESS,
            payload=payload,
            execution_time_ms=execution_time_ms
        )
    
    @classmethod
    def failure_result(cls, result_code: ValidationResult, error_details: str = None, 
                      execution_time_ms: float = None, debug_info: Dict[str, Any] = None) -> 'AuthResult':
        """创建失败结果"""
        return cls(
            success=False,
            result_code=result_code,
            error_details=error_details,
            execution_time_ms=execution_time_ms,
            debug_info=debug_info
        )


# ==================== 插件接口 ====================

@runtime_checkable
class FingerprintValidator(Protocol):
    """设备指纹验证器接口"""
    
    def validate(self, payload: Dict[str, Any], logger_func: callable = None) -> bool:
        """验证设备指纹"""
        ...


class DpflaskFingerprintValidator:
    """dpflask风格设备指纹验证器"""
    
    def validate(self, payload: Dict[str, Any], logger_func: callable = None) -> bool:
        """验证设备指纹"""
        try:
            client_data = payload.get('deviceData', {})
            client_hash = payload.get('deviceHash', '')
            
            if not client_hash:
                if logger_func:
                    logger_func("设备指纹哈希为空")
                return False

            def deep_sort(obj):
                if isinstance(obj, dict):
                    return {k: deep_sort(v) for k, v in sorted(obj.items(), key=lambda x: x)}
                if isinstance(obj, list):
                    return sorted((deep_sort(x) for x in obj),
                                  key=lambda x: (isinstance(x, (int, float)), x))
                return obj

            # 严格类型转换保证与前端一致
            standardized_data = deep_sort({
                "userAgent": str(client_data.get("userAgent", "")),
                "platform": str(client_data.get("platform", "")),
                "languages": sorted([str(x) for x in client_data.get("languages", [])]),
                "hardwareConcurrency": int(client_data.get("hardwareConcurrency", 0)),
                "screenProps": {
                    "width": int(client_data.get("screenProps", {}).get("width", 0)),
                    "height": int(client_data.get("screenProps", {}).get("height", 0)),
                    "colorDepth": int(client_data.get("screenProps", {}).get("colorDepth", 0))
                }
            })

            # JSON序列化
            class CompactJSONEncoder(json.JSONEncoder):
                def encode(self, obj):
                    return json.dumps(obj, separators=(',', ':'), sort_keys=False)

            data_str = CompactJSONEncoder().encode(standardized_data)
            
            # SHA512哈希
            sha512 = hashlib.sha512()
            sha512.update(data_str.encode('utf-8'))
            server_hash_str = sha512.hexdigest()

            # 常量时间比较
            if not hmac.compare_digest(server_hash_str.encode(), client_hash.encode()):
                if logger_func:
                    logger_func(f"设备指纹不匹配: 期望长度={len(server_hash_str)}, 实际长度={len(client_hash)}")
                return False

            # 硬件验证
            hw_concurrency = standardized_data["hardwareConcurrency"]
            if not (1 <= hw_concurrency <= 128 and isinstance(hw_concurrency, int)):
                if logger_func:
                    logger_func(f"硬件并发数异常: {hw_concurrency}")
                return False

            screen = standardized_data["screenProps"]
            if not all(isinstance(v, int) and v > 0 for v in [screen["width"], screen["height"], screen["colorDepth"]]):
                if logger_func:
                    logger_func(f"屏幕属性异常: {screen}")
                return False

            return True

        except Exception as e:
            if logger_func:
                logger_func(f"设备指纹验证异常: {str(e)}")
            return False


class CryptoManager:
    """
    通用加密解密管理器
    """
    
    def __init__(self, 
                 config: CryptoConfig,
                 redis_client=None,
                 fingerprint_validator: Optional[FingerprintValidator] = None):
        """
        初始化加密管理器
        
        Args:
            config: 加密配置对象（必需）
            logger: 日志记录器，None时不使用日志
            redis_client: Redis客户端，用于nonce防重放攻击
            fingerprint_validator: 设备指纹验证器，None时使用默认dpflask验证器
        """
        self.config = config
        self.redis_client = redis_client
        self.enable_nonce_check = self.config.enable_nonce_check and redis_client is not None
        self.fingerprint_validator = fingerprint_validator or DpflaskFingerprintValidator()
        
        self._init_redis()
        # 密钥缓存初始化
        self._init_cache()
        
        # 验证环境
        self._validate_environment()
        
        logger.debug(f"CryptoManager初始化完成: keys_dir={self.keys_directory}, nonce_enabled={self.enable_nonce_check}")
    
    def _init_redis(self):
        """初始化Redis"""
        if not self.redis_client:
            redis_password = parser.get_value(file_path=config_file, section='redis', key='password', value_type=str)  # redis 使用本地数据，全部机子相同
            # Redis连接配置, 创建连接池
            import redis
            redis_pool = redis.ConnectionPool(
                host='127.0.0.1',
                port=6379,
                db=0,
                password=redis_password,
                max_connections=3,  # 连接池最大连接数
                socket_timeout=5,  # 操作超时时间（秒）
                socket_connect_timeout=3,  # 连接超时时间（秒）
                health_check_interval=30,  # 健康检查间隔（秒）
                decode_responses=False,  # 保持二进制数据格式
            )

            # 通过连接池获取Redis实例，这个实例用于密钥服务
            self.redis_client = redis.Redis(connection_pool=redis_pool)

    def _init_cache(self) -> None:
        """初始化密钥缓存"""
        self._key_cache_lock = threading.RLock()
        self._public_key_cache = None
        self._private_key_cache = None
        self._cache_timestamp = 0
        
        # 构建密钥目录路径
        self.keys_directory = os.path.join(self.config.key_dir_path, self.config.keys_subdir)
    
    def _validate_environment(self) -> None:
        """验证运行环境"""
        # 验证密钥目录
        if not os.path.exists(self.keys_directory):
            error_msg = f"密钥目录不存在: {self.keys_directory}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
    
    # ==================== 缓存管理方法 ====================
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.config.enable_key_cache:
            return False
        current_time = time.time()
        return (self._cache_timestamp > 0 and 
                current_time - self._cache_timestamp < self.config.key_cache_ttl_seconds)
    
    def clear_cache(self) -> None:
        """清除密钥缓存"""
        with self._key_cache_lock:
            self._public_key_cache = None
            self._private_key_cache = None
            self._cache_timestamp = 0
            logger.debug("密钥缓存已清除")
    
    # ==================== 密钥加载方法 ====================
    
    def _load_public_key_from_file(self) -> Optional[str]:
        """从文件加载公钥"""
        try:
            key_path = os.path.join(self.keys_directory, f'{self.config.public_key_filename}.pem')
            
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"公钥文件不存在: {key_path}")
            
            with open(key_path, "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
            
            # 转换为 PEM 格式字节
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return public_pem.decode("utf-8")
            
        except Exception as e:
            logger.error(f"公钥加载失败: {str(e)}")
            return None
    
    def _load_private_key_from_file(self):
        """从文件加载私钥"""
        try:
            key_path = os.path.join(self.keys_directory, f'{self.config.private_key_filename}.pem')
            
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"私钥文件不存在: {key_path}")
            
            with open(key_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            
            return private_key
            
        except Exception as e:
            logger.error(f"私钥加载失败: {str(e)}")
            return None
    
    # ==================== 公共API方法 ====================
    
    def get_public_key(self) -> Optional[str]:
        """
        获取PEM格式的公钥字符串（支持缓存）
        """
        with self._key_cache_lock:
            # 检查缓存
            if self._is_cache_valid() and self._public_key_cache is not None:
                logger.debug("使用缓存的公钥")
                return self._public_key_cache
            
            # 从文件加载
            public_key = self._load_public_key_from_file()
            
            # 更新缓存
            if public_key and self.config.enable_key_cache:
                self._public_key_cache = public_key
                self._cache_timestamp = time.time()
                logger.debug("公钥已缓存")
            
            return public_key
    
    def get_keys_info(self) -> Dict[str, Any]:
        """
        获取密钥文件信息
        """
        public_key_path = os.path.join(self.keys_directory, f'{self.config.public_key_filename}.pem')
        private_key_path = os.path.join(self.keys_directory, f'{self.config.private_key_filename}.pem')
        
        return {
            'keys_directory': self.keys_directory,
            'public_key_path': public_key_path,
            'private_key_path': private_key_path,
            'public_key_exists': os.path.exists(public_key_path),
            'private_key_exists': os.path.exists(private_key_path),
            'public_key_size': os.path.getsize(public_key_path) if os.path.exists(public_key_path) else 0,
            'private_key_size': os.path.getsize(private_key_path) if os.path.exists(private_key_path) else 0,
            'cache_enabled': self.config.enable_key_cache,
            'cache_ttl_seconds': self.config.key_cache_ttl_seconds,
            'nonce_enabled': self.enable_nonce_check
        }
    
    # ==================== 核心加解密方法 ====================
    
    def decrypt_payload(self, encrypted_token: str) -> Optional[Dict[str, Any]]:
        """
        解密载荷数据
        """
        try:
            if not encrypted_token:
                logger.warning("加密令牌为空")
                return None
            
            # 获取私钥（使用缓存）
            with self._key_cache_lock:
                if self._is_cache_valid() and self._private_key_cache is not None:
                    logger.debug("使用缓存的私钥")
                    private_key = self._private_key_cache
                else:
                    private_key = self._load_private_key_from_file()
                    if not private_key:
                        return None
                    
                    # 更新缓存
                    if self.config.enable_key_cache:
                        self._private_key_cache = private_key
                        if self._cache_timestamp == 0:  # 首次缓存时间戳
                            self._cache_timestamp = time.time()
                        logger.debug("私钥已缓存")
            
            # 解析加密令牌
            try:
                token_data = json.loads(base64.b64decode(encrypted_token).decode())
            except (json.JSONDecodeError, ValueError, base64.binascii.Error) as e:
                logger.warning(f"令牌格式错误: {type(e).__name__}")
                return None
            
            # 验证令牌格式
            required_fields = ['key', 'iv', 'ciphertext', 'tag']
            missing_fields = [field for field in required_fields if field not in token_data]
            if missing_fields:
                logger.warning(f"令牌缺少必需字段: {missing_fields}")
                return None
            
            # 解码各个组件
            try:
                encrypted_key = base64.b64decode(token_data['key'])
                iv = base64.b64decode(token_data['iv'])
                ciphertext = base64.b64decode(token_data['ciphertext'])
                tag = base64.b64decode(token_data['tag'])
            except (ValueError, base64.binascii.Error) as e:
                logger.warning(f"令牌组件Base64解码失败: {type(e).__name__}")
                return None
            
            # 使用RSA-OAEP解密AES密钥
            try:
                raw_key = private_key.decrypt(
                    encrypted_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA512()),
                        algorithm=hashes.SHA512(),
                        label=None
                    )
                )
            except Exception as e:
                logger.warning(f"RSA解密失败: {type(e).__name__}")
                return None
            
            # 使用AES-GCM解密载荷数据
            try:
                aesgcm = AESGCM(raw_key)
                decrypted = aesgcm.decrypt(iv, ciphertext + tag, None)
            except Exception as e:
                logger.warning(f"AES-GCM解密失败: {type(e).__name__}")
                return None
            
            # 解析JSON载荷
            try:
                payload = json.loads(decrypted.decode())
                logger.debug("载荷解密成功")
                return payload
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"载荷JSON解析失败: {type(e).__name__}")
                return None
            
        except Exception as e:
            logger.error(f"解密载荷异常: {str(e)}")
            return None
    
    def validate_payload(self, payload: Dict[str, Any], token: Optional[str] = None) -> bool:
        """
        验证载荷数据的完整性和有效性
        """
        try:
            if not isinstance(payload, dict):
                return False
            
            # 1. 时间窗口验证
            current_time = int(time.time())
            payload_timestamp = payload.get('timestamp', 0)
            
            if not isinstance(payload_timestamp, (int, float)):
                return False
            
            time_diff = abs(current_time - int(payload_timestamp))
            if time_diff > self.config.time_window_seconds:
                return False
            
            # 2. 设备指纹验证
            def log_fingerprint_error(msg):
                logger.warning(f"设备指纹验证: {msg}")
            
            if not self.fingerprint_validator.validate(payload, log_fingerprint_error):
                return False
            
            # 3. nonce验证
            if self.enable_nonce_check and token:
                nonce = payload.get('nonce')
                if not nonce:
                    return False
                
                if self._is_nonce_used(nonce, token):
                    return False
            
            logger.debug("载荷验证通过")
            return True
            
        except Exception as e:
            logger.error(f"验证载荷异常: {str(e)}")
            return False
    
    def _is_nonce_used(self, nonce: str, token: str) -> bool:
        """
        防重放攻击检查
        """
        if not self.enable_nonce_check or not self.redis_client:
            return False
            
        try:
            redis_key = f"{self.config.nonce_redis_prefix}:{nonce}"
            # 原子操作：设置键值并设置过期时间
            result = self.redis_client.set(
                name=redis_key,
                value=token,
                ex=self.config.nonce_expire_seconds,
                nx=True  # 仅当键不存在时设置
            )
            is_used = not bool(result)  # False表示设置成功（未使用过）
            if is_used:
                logger.warning(f"nonce重复使用: {nonce[:8]}...")
            return is_used
        except Exception as e:
            logger.error(f"nonce检查异常: {str(e)}")
            return True  # 异常时认为已使用，拒绝请求
    
    # ==================== 高级认证方法 ====================
    
    def get_private_key(self, token: str) -> bool:
        """
        加载私钥并解密令牌进行校检（dpflask兼容方法）
        这是dpflask风格的一体化验证方法：解密+验证一步完成
        """
        result = self.authenticate_token_detailed(token)
        return result.success
    
    def authenticate_token(self, token: str) -> Dict[str, Any]:
        """
        认证令牌并返回详细结果（向后兼容）
        """
        result = self.authenticate_token_detailed(token)
        return {
            'success': result.success,
            'error': result.result_code.value if not result.success else None,
            'message': result.error_details or ('认证成功' if result.success else '认证失败'),
            'payload': result.payload
        }
    
    def authenticate_token_detailed(self, token: str) -> AuthResult:
        """
        认证令牌并返回标准化结果对象
        """
        start_time = time.time()
        
        try:
            if not token:
                return AuthResult.failure_result(
                    ValidationResult.INVALID_PAYLOAD,
                    "令牌为空",
                    (time.time() - start_time) * 1000
                )
            
            # 1. 解密载荷
            payload = self.decrypt_payload(token)
            if not payload:
                return AuthResult.failure_result(
                    ValidationResult.DECRYPT_FAILED,
                    "令牌解密失败",
                    (time.time() - start_time) * 1000
                )
            
            # 2. 验证载荷
            if not self.validate_payload(payload, token):
                # 根据验证失败的具体原因返回不同的结果码
                current_time = int(time.time())
                payload_timestamp = payload.get('timestamp', 0)
                
                if abs(current_time - int(payload_timestamp)) > self.config.time_window_seconds:
                    return AuthResult.failure_result(
                        ValidationResult.TIMESTAMP_INVALID,
                        "时间窗口验证失败",
                        (time.time() - start_time) * 1000
                    )
                
                # 检查nonce
                if self.enable_nonce_check and token:
                    nonce = payload.get('nonce')
                    if nonce and self._is_nonce_used(nonce, token):
                        return AuthResult.failure_result(
                            ValidationResult.NONCE_REUSED,
                            "nonce重复使用",
                            (time.time() - start_time) * 1000
                        )
                
                # 其他情况（设备指纹验证失败等）
                return AuthResult.failure_result(
                    ValidationResult.FINGERPRINT_MISMATCH,
                    "设备指纹验证失败",
                    (time.time() - start_time) * 1000
                )
            
            # 3. 验证成功
            execution_time = (time.time() - start_time) * 1000
            logger.debug(f"令牌认证成功，耗时: {execution_time:.2f}ms")
            
            return AuthResult.success_result(payload, execution_time)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"令牌认证异常: {str(e)}")
            
            return AuthResult.failure_result(
                ValidationResult.DECRYPT_FAILED,
                f"认证异常: {str(e)}",
                execution_time,
                {"exception_type": type(e).__name__}
            )
    
    def get_keys_info(self) -> Dict[str, Any]:
        """
        获取密钥文件信息
        """
        public_key_path = os.path.join(self.keys_directory, f'{self.config.public_key_filename}.pem')
        private_key_path = os.path.join(self.keys_directory, f'{self.config.private_key_filename}.pem')
        
        return {
            'keys_directory': self.keys_directory,
            'public_key_path': public_key_path,
            'private_key_path': private_key_path,
            'public_key_exists': os.path.exists(public_key_path),
            'private_key_exists': os.path.exists(private_key_path),
            'public_key_size': os.path.getsize(public_key_path) if os.path.exists(public_key_path) else 0,
            'private_key_size': os.path.getsize(private_key_path) if os.path.exists(private_key_path) else 0,
            'cache_enabled': self.config.enable_key_cache,
            'cache_ttl_seconds': self.config.key_cache_ttl_seconds,
            'nonce_enabled': self.enable_nonce_check
        }


class CryptoHelper:
    """
    加密工具辅助类
    """
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        生成安全的随机令牌
        
        Args:
            length (int): 令牌长度，默认32字节
        
        Returns:
            str: 十六进制格式的随机令牌
        """
        import secrets
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_data(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        对数据进行哈希处理
        
        Args:
            data (str|bytes): 要哈希的数据
            algorithm (str): 哈希算法，支持 'md5', 'sha1', 'sha256', 'sha512'
        
        Returns:
            str: 十六进制格式的哈希值
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_func = getattr(hashlib, algorithm.lower())()
        hash_func.update(data)
        return hash_func.hexdigest()
    
    @staticmethod
    def encode_base64(data: Union[str, bytes]) -> str:
        """
        Base64编码
        
        Args:
            data (str|bytes): 要编码的数据
        
        Returns:
            str: Base64编码后的字符串
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def decode_base64(encoded_data: str) -> bytes:
        """
        Base64解码
        
        Args:
            encoded_data (str): Base64编码的字符串
        
        Returns:
            bytes: 解码后的字节数据
        """
        return base64.b64decode(encoded_data)


if __name__ == "__main__":
    pass
