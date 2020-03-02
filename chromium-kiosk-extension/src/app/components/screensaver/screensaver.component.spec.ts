import { TestBed, async } from '@angular/core/testing';
import { ScreensaverComponent } from './screensaver.component';

describe('ScreensaverComponent', () => {
  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        ScreensaverComponent
      ],
    }).compileComponents();
  }));

  it('should create the app', () => {
    const fixture = TestBed.createComponent(ScreensaverComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  });

  it(`should have as title 'angular-chrome-extension'`, () => {
    const fixture = TestBed.createComponent(ScreensaverComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app.title).toEqual('angular-chrome-extension');
  });

  it('should render title', () => {
    const fixture = TestBed.createComponent(ScreensaverComponent);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('.content span').textContent).toContain('angular-chrome-extension app is running!');
  });
});
