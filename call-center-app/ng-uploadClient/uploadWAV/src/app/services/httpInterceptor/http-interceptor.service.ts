import { Injectable } from '@angular/core';
import { HTTP_INTERCEPTORS} from "@angular/common/http";
import { HttpInterceptor, HttpHandler, HttpRequest} from "@angular/common/http";
import { TokenStorageService } from "../tokenStorage/token-storage.service";

const TOKEN_HEADER_KEY = 'Authorization';


@Injectable({
  providedIn: 'root'
})
export class HttpInterceptorService implements HttpInterceptor {

  constructor(private tokenStorageService: TokenStorageService) { }

  intercept(req: HttpRequest<any>, next: HttpHandler) {
    let authReq = req;
    const token = this.tokenStorageService.getToken();
    if (token != null) {
      authReq = req.clone({ headers: req.headers.set(TOKEN_HEADER_KEY, 'Bearer ' + token) });
    }
    console.log('token in interceptor is' + token);

    return next.handle(authReq);
  }

}

export const authInterceptorProviders = [
  { provide: HTTP_INTERCEPTORS, useClass: HttpInterceptorService, multi: true }
];
