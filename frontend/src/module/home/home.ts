import { Component } from '@angular/core';
import { Card } from 'primeng/card';
import { Divider } from 'primeng/divider';
import { InputText } from 'primeng/inputtext';
import { Button } from 'primeng/button';


@Component({
  selector: 'app-home',
  imports: [Button, Card, Divider],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {

}
