use crate::{error::APIError, Error, Result};
use axum::{
    body::Body,
    extract::Request,
    handler::Handler,
    http::{Response, StatusCode},
};

//pub async fn auth_middleware(req: Request<Body>, handler: Handler) -> Result<Response<Body>> {
//    let auth_header = req.headers().get("Authorization");
//    let auth_header = match auth_header {
//        Some(header) => header.to_str().map_err(|_| {
//            Error::AuthError(APIError {
//                status_code: StatusCode::UNAUTHORIZED,
//                message: "Invalid Authorization header".to_string(),
//            })
//        })?,
//        None => {
//            return Err(Error::AuthError(APIError {
//                status_code: StatusCode::UNAUTHORIZED,
//                message: "Missing Authorization header".to_string(),
//            }))
//        }
//    };
//}
