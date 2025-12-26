export interface PageRequest {
    page: number;
    size: number;
    sort?: string;
}


export function toPageRequest(
    first: number | null | undefined,
    rows: number | null | undefined,
    sort?: string
): PageRequest {
    const size = rows ?? 10;
    const page = Math.floor((first ?? 0) / size);

    return { page, size, sort };
}
