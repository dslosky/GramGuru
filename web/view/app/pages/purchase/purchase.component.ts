import { Component, AfterViewInit } from '@angular/core';
import { PurchaseService } from './purchase.service'
declare var Stripe: any;

@Component({
  selector: 'purchase',
  templateUrl: 'app/pages/purchase/purchase.component.html',
  styleUrls: ['app/pages/purchase/purchase.component.css']
})
export class PurchaseComponent implements AfterViewInit {
    public stripe: any = Stripe('pk_test_OlynsWFay14tzZvc6Hzg4sEV');
    public card: any = null;
    public selected: string = '1month'

    constructor(private pService: PurchaseService) {}
    ngAfterViewInit() {

        // Create an instance of Elements
        var elements = this.stripe.elements();

        // Create an instance of the card Element
        this.card = elements.create('card');

        // Add an instance of the card Element into the `card-element` <div>
        this.card.mount('#card-element');

        // Handle real-time validation errors from the card Element.
        this.card.addEventListener('change', function(event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
        });
    }

    submit() {
        // Handle form submission
        this.stripe.createToken(this.card).then((result: any) => {
            if (result.error) {
                // Inform the user if there was an error
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
            } else {
                // Send the token to your server
                this.pService.purchase(this.selected, result.token);
            }
        });
    }
}