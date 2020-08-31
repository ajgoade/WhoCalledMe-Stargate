import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TokenStorageService {

  jwtToken: string;

  constructor() { }

  storeToken(newJwt) {
    this.jwtToken=newJwt;
  }

  getToken() {
    return this.jwtToken;
  }

}
