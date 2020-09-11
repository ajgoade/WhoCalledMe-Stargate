import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LoginComponent} from "./components/login/login.component";
import {UploadComponent} from "./components/upload/upload.component";

const routes: Routes = [
  { path: 'login', component: LoginComponent},
  { path: 'upload', component: UploadComponent}

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
  declarations: [
  ]
})
export class AppRoutingModule { }
