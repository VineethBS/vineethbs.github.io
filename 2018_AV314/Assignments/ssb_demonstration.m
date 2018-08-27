fs = 40000;
Tmax = 5;
t = 0:(1/fs):Tmax;

%% Make an example of the message signal
% c = [1, 4, 3, 5];
% f = [10, 20, 50, 100];
c = [1];
f = [50];

m = zeros(1, length(t));

for i = 1:length(c)
    m = m + c(i) * cos(2 * pi * f(i) * t);
end

% View the message signal and its spectrum
plot(t, m);
plotspectrum(m);
pause

%% Generate the carrier signal - This is what the local oscillator at the transmitter does
A = 1;
fc = 3000;
carrier = A * cos(2 * pi *  fc * t);
% View the spectrum of the carrier
plotspectrum(carrier);
pause

%% Generate the DSB (or DSBSC) signal
dsbsignal_ioft = m .* carrier;
plot(t, dsbsignal_ioft);
plotspectrum(dsbsignal_ioft);
pause;

%% Filter the DSB signal to generate the SSB signal
ssb_bpf = 0; % HOW WILL YOU MODIFY THIS?
tranmsitted_signal = conv(dsbsignal_ioft, ssb_bpf);

%% Channel BPF model 
channel_hoft = BPF_impulseresponse(2500, 3500);
plotspectrum(channel_hoft);
pause;

%% Output from the channel
received_ssbsignal_ooft = conv(transmitted_signal,channel_hoft);
plotspectrum(received_ssbsignal_ooft);
pause;

%% Should have a bandpass filter here - not discussed in class yet


%% Note that t needs to change because of the convolution
tr = 0:(1/fs):(length(received_ssbsignal_ooft)/fs - 1/fs);
%% SSB demodulation - Generate carrier at the receiver local oscillator
A = 1;
fc = 3000;
phase = pi/4;
rx_carrier = A * cos(2 * pi *  fc * tr + phase);

%% Demodulation - Multiply received signal with receiver's local oscillator's carrier
multiplied_output = rx_carrier .* received_ssbsignal_ooft;
plotspectrum(multiplied_output);
pause;

%% Demodulation - low pass filter
lpf = LPF_impulseresponse(120);
mcap = conv(lpf, multiplied_output);
figure(1);
plot((0:(length(mcap) - 1))/fs, mcap, 'r');
hold on;
plot(t, m, 'k');

plotspectrum(mcap);
pause;
