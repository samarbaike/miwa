const BASE_URL = import.meta.env.VITE_API_URL;

class apiError extends Error {
    status: number;
    detail: unknown;

    constructor(
        message: string,
        status: number,
        detail: unknown
    ) {
        super(message);
        this.name = "apiError";
        this.status = status;
        this.detail = detail
    }
}

async function apiClient<T>(
    endpoint : string, 
    options : RequestInit = {}
) : Promise<T> {
    const url = `${BASE_URL}${endpoint}`;

    const defaultHeader = {
        "Content-Type":"application/json",
        ...options.headers
    };

    const config : RequestInit = {
        ...options,
        headers:defaultHeader,
        credentials : "include",
    }

    if (options.body && typeof options.body === "object") {
        config.body = JSON.stringify(options.body)
    }

    const response = await fetch(url, config);

    if (!response.ok) {
        let errorMessage = "An error occured";
        let errorDetail = null;

        try {
            const errorData = await response.json();
            errorDetail = errorData.detail;

            //handle FastAPI's 422 array structure or/and string errors
            if (Array.isArray(errorDetail)) {
                errorMessage = errorDetail.map(err => `${err.loc.join(".")}: ${err.msg}`).join(", ");
            } else if (typeof errorDetail === 'string'){
                errorMessage = errorDetail;
            }
        } catch {
            //Fallback if server didn't return json
            errorMessage = response.statusText;
        }

        const error = new apiError(
            errorMessage,
            response.status,
            errorDetail
        );
        throw error
    }
    return response.json()
};

export default apiClient