import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import {AuthService} from "../../services/authService/auth.service";
import {TokenStorageService} from "../../services/tokenStorage/token-storage.service";
import {Router} from "@angular/router";
import {UserService} from "../../services/user/user.service";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  loginSuccessful: boolean  = false;
  loginMessage: string = 'Please enter credentials to login';

  user:FormControl;
  password: FormControl;

  constructor(private authService: AuthService,
              private tokenStorageService: TokenStorageService,
              private router: Router,
              private userService: UserService) { }

  ngOnInit(): void {
    this.user = new FormControl('');
    this.password = new FormControl('');
  }

  tryLogin() {
    console.debug('login request|user=' + this.user.value + '|password=' + this.password.value);

    this.authService.login({username:this.user.value, password:this.password.value})
      .subscribe((result) => {

        console.log(result.body);
        console.log("jwt|" + result.jwt);
        this.tokenStorageService.storeToken(result.jwt);

        this.userService.setUserName(this.user.value);

        this.loginSucceeded();
      }, (errData) => {

        console.error(errData);
        this.loginFailed();
      });

  }

  loginSucceeded() {
    this.router.navigate(['/upload']);
    return this.loginSuccessful;
  }

  loginFailed() {
    this.loginMessage = "Could not authenticate you; please re-enter user ID and password";
    return !this.loginSuccessful;
  }


}
