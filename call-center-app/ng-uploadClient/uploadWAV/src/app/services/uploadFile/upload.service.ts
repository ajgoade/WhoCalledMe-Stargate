import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import {TokenStorageService} from "../tokenStorage/token-storage.service";

const AUTH_API = 'http://localhost:3030/files/';

let httpOptions = {

};


@Injectable({
  providedIn: 'root'
})
export class UploadService {

  constructor(public httpClient: HttpClient,
              public tokenStorageService: TokenStorageService
              ) { }

  public uploadFile(soundFile, user, fileName) {
    const formData = new FormData();
    formData.append('audio_message', soundFile, fileName);

    httpOptions = {
      headers: new HttpHeaders({
        'Authorization': 'Bearer ' + this.tokenStorageService.getToken(),
        reportProgress: 'true',
        observe: 'events'
      })
    };

    return this.httpClient.post(AUTH_API, formData, httpOptions);

  }

}
