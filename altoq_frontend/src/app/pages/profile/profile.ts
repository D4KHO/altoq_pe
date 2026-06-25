import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { Address, AddressCreate, UserUpdate, PasswordChange } from '../../models/user-profile';
import { User } from '../../models/auth';
import { MapboxService } from '../../services/mapbox.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class ProfileComponent implements OnInit {
  user: User | null = null;
  addresses: Address[] = [];

  activeTab: 'profile' | 'password' | 'addresses' = 'profile';

  profileForm: FormGroup;
  passwordForm: FormGroup;
  addressForm: FormGroup;

  loading = false;
  message = '';
  error = '';

  editingAddress: Address | null = null;
  showAddressForm = false;

  // Variables para Mapbox
  showMapModal = false;
  map: any = null;
  marker: any = null;
  selectedLatitude: number | null = null;
  selectedLongitude: number | null = null;

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private authService: AuthService,
    private mapboxService: MapboxService
  ) {
    this.profileForm = this.fb.group({
      name: ['', Validators.required],
      phone: ['']
    });

    this.passwordForm = this.fb.group({
      old_password: ['', Validators.required],
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirm_password: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });

    this.addressForm = this.fb.group({
      name: [''],
      street: ['', Validators.required],
      city: ['', Validators.required],
      state: [''],
      postal_code: [''],
      country: ['Peru'],
      phone: [''],
      is_default: [false],
      latitude: [null],
      longitude: [null]
    });
  }

  ngOnInit() {
    this.authService.user$.subscribe(user => {
      if (user) {
        this.user = user;
        this.profileForm.patchValue({
          name: user.name,
          phone: user.phone || ''
        });
      }
    });

    this.loadProfile();
    this.loadAddresses();
  }

  passwordMatchValidator(g: FormGroup) {
    return g.get('new_password')?.value === g.get('confirm_password')?.value
      ? null : { mismatch: true };
  }

  setTab(tab: 'profile' | 'password' | 'addresses') {
    this.activeTab = tab;
    this.message = '';
    this.error = '';
  }

  // ===== PROFILE =====

  loadProfile() {
    this.loading = true;
    this.userService.getProfile().subscribe({
      next: (user) => {
        this.user = user;
        this.profileForm.patchValue({
          name: user.name,
          phone: user.phone || ''
        });
        this.loading = false;
      },
      error: (err) => {
        if (!this.user) {
          this.error = 'Error al cargar perfil';
        }
        this.loading = false;
      }
    });
  }

  updateProfile() {
    if (this.profileForm.invalid) return;

    this.loading = true;
    const data: UserUpdate = this.profileForm.value;

    this.userService.updateProfile(data).subscribe({
      next: (user) => {
        this.user = user;
        this.authService.user$.subscribe(currentUser => {
          if (currentUser) {
            const updated = { ...currentUser, name: user.name, phone: user.phone };
            localStorage.setItem('user', JSON.stringify(updated));
          }
        });
        this.message = 'Perfil actualizado correctamente';
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al actualizar perfil';
        this.loading = false;
      }
    });
  }

  // ===== PASSWORD =====

  changePassword() {
    if (this.passwordForm.invalid) return;

    this.loading = true;
    const data: PasswordChange = {
      old_password: this.passwordForm.value.old_password,
      new_password: this.passwordForm.value.new_password
    };

    this.userService.changePassword(data).subscribe({
      next: (response) => {
        this.message = response.message;
        this.passwordForm.reset();
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error al cambiar contraseña';
        this.loading = false;
      }
    });
  }

  // ===== ADDRESSES =====

  loadAddresses() {
    this.userService.getAddresses().subscribe({
      next: (addresses) => {
        this.addresses = addresses;
      },
      error: (err) => {
        console.log('Could not load addresses:', err);
      }
    });
  }

  openAddressForm(address?: Address) {
    this.editingAddress = address || null;
    this.showAddressForm = true;

    if (address) {
      this.addressForm.patchValue(address);
    } else {
      this.addressForm.reset({ country: 'Peru', is_default: false });
    }
  }

  openMapModal() {
    this.showMapModal = true;
    setTimeout(() => {
      this.initMap();
    }, 100);
  }

  initMap() {
    const lat = this.addressForm.get('latitude')?.value || -5.1945;
    const lng = this.addressForm.get('longitude')?.value || -80.6300;

    const mapboxgl = (window as any).mapboxgl;
    if (!mapboxgl) {
      console.error('Mapbox GL JS library not loaded');
      return;
    }

    mapboxgl.accessToken = this.mapboxService.getToken();

    this.map = new mapboxgl.Map({
      container: 'profileMap',
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [Number(lng), Number(lat)],
      zoom: 15
    });

    this.marker = new mapboxgl.Marker({
      draggable: true
    })
      .setLngLat([Number(lng), Number(lat)])
      .addTo(this.map);

    this.selectedLatitude = Number(lat);
    this.selectedLongitude = Number(lng);

    this.marker.on('dragend', () => {
      const lngLat = this.marker.getLngLat();
      this.selectedLatitude = lngLat.lat;
      this.selectedLongitude = lngLat.lng;
    });

    if (!this.addressForm.get('latitude')?.value) {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const currentLat = position.coords.latitude;
            const currentLng = position.coords.longitude;
            this.map.setCenter([currentLng, currentLat]);
            this.marker.setLngLat([currentLng, currentLat]);
            this.selectedLatitude = currentLat;
            this.selectedLongitude = currentLng;
          },
          () => {}
        );
      }
    }
  }

  confirmMapLocation() {
    if (this.selectedLatitude && this.selectedLongitude) {
      this.addressForm.patchValue({
        latitude: this.selectedLatitude,
        longitude: this.selectedLongitude
      });

      this.mapboxService.reverseGeocode(this.selectedLongitude, this.selectedLatitude).subscribe({
        next: (res: any) => {
          if (res && res.features && res.features.length > 0) {
            const feature = res.features[0];
            let street = feature.place_name || '';
            let city = 'Piura';
            let state = 'Piura';

            if (feature.context) {
              for (const ctx of feature.context) {
                if (ctx.id.startsWith('place')) {
                  city = ctx.text;
                } else if (ctx.id.startsWith('region')) {
                  state = ctx.text;
                }
              }
            }

            if (feature.text) {
              street = feature.text + (feature.address ? ' ' + feature.address : '');
            }

            this.addressForm.patchValue({
              street: street,
              city: city,
              state: state,
              postal_code: ''
            });
          }
          this.showMapModal = false;
        },
        error: (err: any) => {
          console.error(err);
          this.showMapModal = false;
        }
      });
    } else {
      this.showMapModal = false;
    }
  }

  closeAddressForm() {
    this.showAddressForm = false;
    this.editingAddress = null;
    this.addressForm.reset({ country: 'Peru', is_default: false });
    this.message = '';
    this.error = '';
  }

  saveAddress() {
    if (this.addressForm.invalid) return;

    this.loading = true;
    const data: AddressCreate = this.addressForm.value;

    if (this.editingAddress) {
      this.userService.updateAddress(this.editingAddress.id, data).subscribe({
        next: () => {
          this.loadAddresses();
          this.closeAddressForm();
          this.message = 'Dirección actualizada';
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Error al actualizar dirección';
          this.loading = false;
        }
      });
    } else {
      this.userService.createAddress(data).subscribe({
        next: () => {
          this.loadAddresses();
          this.closeAddressForm();
          this.message = 'Dirección agregada';
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Error al agregar dirección';
          this.loading = false;
        }
      });
    }
  }

  deleteAddress(id: number) {
    if (!confirm('¿Estás seguro de eliminar esta dirección?')) return;

    this.userService.deleteAddress(id).subscribe({
      next: () => {
        this.loadAddresses();
        this.message = 'Dirección eliminada';
      },
      error: (err) => {
        this.error = 'Error al eliminar dirección';
      }
    });
  }

  setDefaultAddress(address: Address) {
    this.userService.updateAddress(address.id, { is_default: true }).subscribe({
      next: () => {
        this.loadAddresses();
        this.message = 'Dirección predeterminada actualizada';
      },
      error: (err) => {
        this.error = 'Error al actualizar dirección';
      }
    });
  }

}
