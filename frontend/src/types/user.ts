export interface UserRegister {
    username : string;
    email : string;
    password : string
}

export interface LoginRequest {
    username: string;
    password: string
}

export interface UserResponse {
    id: number;
    username: string;
    email: string;
    elo: number
}

export interface UserStats {
    elo: number;
    win: number;
    streak: number;
    total_matches: number 
}

export interface UserUpdate {
    username: string | null 
}