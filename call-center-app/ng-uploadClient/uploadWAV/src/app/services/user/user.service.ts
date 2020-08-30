import { Injectable } from '@angular/core';


@Injectable({
  providedIn: 'root'
})
export class UserService {

  userName:string;

  constructor() { }

  public setUserName(userName) {
    this.userName = userName;
  }

  public getUserName() {
    return this.userName;
  }

}
