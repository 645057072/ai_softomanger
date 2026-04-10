/**
 * 规范化 JWT 字符串（去掉 Bearer 前缀与空白），供登录写入与请求头共用
 */
export function normalizeAccessToken(raw) {
  if (raw == null) return ''
  let t = String(raw).trim()
  if (/^bearer\s+/i.test(t)) {
    t = t.replace(/^bearer\s+/i, '').trim()
  }
  return t
}
