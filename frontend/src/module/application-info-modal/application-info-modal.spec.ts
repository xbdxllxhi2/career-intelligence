import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApplicationInfoModal } from './application-info-modal';

describe('ApplicationInfoModal', () => {
  let component: ApplicationInfoModal;
  let fixture: ComponentFixture<ApplicationInfoModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApplicationInfoModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ApplicationInfoModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
