# 测试组织机构 API
$loginBody = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "http://47.93.44.247/api/auth/login" -Method POST -ContentType "application/json" -Body $loginBody
$loginData = $loginResponse.Content | ConvertFrom-Json
$token = $loginData.data.access_token

$headers = @{
    "Authorization" = "Bearer $token"
}

Write-Host "Testing Organization API..."
try {
    $orgResponse = Invoke-WebRequest -Uri "http://47.93.44.247/api/organization?page=1&per_page=1" -Method GET -Headers $headers
    Write-Host "Success!"
    Write-Host $orgResponse.Content
} catch {
    Write-Host "Error:"
    Write-Host $_.Exception.Response.StatusCode
    Write-Host $_.ErrorDetails.Message
}
