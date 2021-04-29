<div *ngIf="isShowDetAsi">
    <p-dialog header="Detalles del asiento" [style]="{width: '90vw'}" [autoZIndex]="false"
              [modal]="true"
              [closeOnEscape]="true"
              [(visible)]="isShowDetAsi">
        <app-asientoview [trncod]="asisel.trn_codigo" (evCerrar)="hideDetAsi()"></app-asientoview>
    </p-dialog>
</div>



<p-dialog header="Detalles del documento" [modal]="true" [style]="{width: '90vw'}" [baseZIndex]="10000"
          [(visible)]="isShowFactura">
    <app-facturaview [trncod]="codFactura" (evBtnClosed)="closeDetallesFact()"
                     (evFacturaLoaded)="onFacturaLoaded($event)"></app-facturaview>
</p-dialog>
