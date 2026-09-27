package com.sentinelai.dto.response;

public class AuthResponse {
    private String token;
    private String type = "Bearer";
    private Long expiresIn;
    private UserResponse user;

    public AuthResponse() {}

    public AuthResponse(String token, Long expiresIn, UserResponse user) {
        this.token = token;
        this.type = "Bearer";
        this.expiresIn = expiresIn;
        this.user = user;
    }

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public Long getExpiresIn() { return expiresIn; }
    public void setExpiresIn(Long expiresIn) { this.expiresIn = expiresIn; }

    public UserResponse getUser() { return user; }
    public void setUser(UserResponse user) { this.user = user; }
}
