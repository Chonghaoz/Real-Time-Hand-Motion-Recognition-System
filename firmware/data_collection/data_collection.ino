#include <Wire.h>
#include <math.h>

#define QMI8658_ADDR 0x6B

#define CTRL1 0x02
#define CTRL2 0x03
#define CTRL3 0x04
#define CTRL7 0x08
#define AX_L  0x35

const float alpha = 0.2f;
const float gravityAlpha = 0.05f;
const int WINDOW_SIZE = 5;

float fax = 0, fay = 0, faz = 0;
float fgx = 0, fgy = 0, fgz = 0;

float gravx = 0, gravy = 0, gravz = 0;

float lastGyroMag = 0.0f;
float lastLinAccMag = 0.0f;

float gyroWindow[WINDOW_SIZE];
float linAccWindow[WINDOW_SIZE];
float linAxWindow[WINDOW_SIZE];
float linAyWindow[WINDOW_SIZE];
float linAzWindow[WINDOW_SIZE];

int windowIndex = 0;
bool windowFilled = false;

void writeRegister(uint8_t reg, uint8_t val) {
  Wire.beginTransmission((uint8_t)QMI8658_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

int16_t read16(uint8_t reg) {
  Wire.beginTransmission((uint8_t)QMI8658_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)QMI8658_ADDR, (uint8_t)2);

  uint8_t low = 0;
  uint8_t high = 0;
  if (Wire.available()) low = Wire.read();
  if (Wire.available()) high = Wire.read();

  return (int16_t)((high << 8) | low);
}

void setupIMU() {
  writeRegister(CTRL1, 0x40);
  delay(50);
  writeRegister(CTRL2, 0x15);
  writeRegister(CTRL3, 0x35);
  writeRegister(CTRL7, 0x03);
  delay(50);
}

void readIMU(float &ax, float &ay, float &az, float &gx, float &gy, float &gz) {
  ax = read16(AX_L) / 16384.0f;
  ay = read16(AX_L + 2) / 16384.0f;
  az = read16(AX_L + 4) / 16384.0f;

  gx = read16(AX_L + 6) / 64.0f;
  gy = read16(AX_L + 8) / 64.0f;
  gz = read16(AX_L + 10) / 64.0f;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(6, 7);
  setupIMU();

  float ax, ay, az, gx, gy, gz;
  readIMU(ax, ay, az, gx, gy, gz);

  fax = ax;
  fay = ay;
  faz = az;

  fgx = gx;
  fgy = gy;
  fgz = gz;

  gravx = ax;
  gravy = ay;
  gravz = az;

  float lin_ax = ax - gravx;
  float lin_ay = ay - gravy;
  float lin_az = az - gravz;

  float initGyroMag = sqrt(fgx * fgx + fgy * fgy + fgz * fgz);
  float initLinAccMag = sqrt(lin_ax * lin_ax + lin_ay * lin_ay + lin_az * lin_az);

  lastGyroMag = initGyroMag;
  lastLinAccMag = initLinAccMag;

  for (int i = 0; i < WINDOW_SIZE; i++) {
    gyroWindow[i] = initGyroMag;
    linAccWindow[i] = initLinAccMag;
    linAxWindow[i] = lin_ax;
    linAyWindow[i] = lin_ay;
    linAzWindow[i] = lin_az;
  }

  Serial.println("gx,gy,gz,lin_acc_mag,gyro_mag,gyro_diff,lin_acc_diff,gyro_avg,gyro_var,lin_acc_avg,lin_acc_var,lin_ax_avg,lin_ay_avg,lin_az_avg");
}

void loop() {
  float ax, ay, az, gx, gy, gz;
  readIMU(ax, ay, az, gx, gy, gz);

  fax = alpha * ax + (1.0f - alpha) * fax;
  fay = alpha * ay + (1.0f - alpha) * fay;
  faz = alpha * az + (1.0f - alpha) * faz;

  fgx = alpha * gx + (1.0f - alpha) * fgx;
  fgy = alpha * gy + (1.0f - alpha) * fgy;
  fgz = alpha * gz + (1.0f - alpha) * fgz;

  gravx = gravityAlpha * fax + (1.0f - gravityAlpha) * gravx;
  gravy = gravityAlpha * fay + (1.0f - gravityAlpha) * gravy;
  gravz = gravityAlpha * faz + (1.0f - gravityAlpha) * gravz;

  float lin_ax = fax - gravx;
  float lin_ay = fay - gravy;
  float lin_az = faz - gravz;

  float lin_acc_mag = sqrt(lin_ax * lin_ax + lin_ay * lin_ay + lin_az * lin_az);
  float gyro_mag = sqrt(fgx * fgx + fgy * fgy + fgz * fgz);

  float gyro_diff = fabs(gyro_mag - lastGyroMag);
  float lin_acc_diff = fabs(lin_acc_mag - lastLinAccMag);

  lastGyroMag = gyro_mag;
  lastLinAccMag = lin_acc_mag;

  gyroWindow[windowIndex] = gyro_mag;
  linAccWindow[windowIndex] = lin_acc_mag;
  linAxWindow[windowIndex] = lin_ax;
  linAyWindow[windowIndex] = lin_ay;
  linAzWindow[windowIndex] = lin_az;

  windowIndex++;

  if (windowIndex >= WINDOW_SIZE) {
    windowIndex = 0;
    windowFilled = true;
  }

  if (!windowFilled) {
    delay(100);
    return;
  }

  float gyro_avg = 0.0f;
  float lin_acc_avg = 0.0f;
  float lin_ax_avg = 0.0f;
  float lin_ay_avg = 0.0f;
  float lin_az_avg = 0.0f;

  for (int i = 0; i < WINDOW_SIZE; i++) {
    gyro_avg += gyroWindow[i];
    lin_acc_avg += linAccWindow[i];
    lin_ax_avg += linAxWindow[i];
    lin_ay_avg += linAyWindow[i];
    lin_az_avg += linAzWindow[i];
  }

  gyro_avg /= WINDOW_SIZE;
  lin_acc_avg /= WINDOW_SIZE;
  lin_ax_avg /= WINDOW_SIZE;
  lin_ay_avg /= WINDOW_SIZE;
  lin_az_avg /= WINDOW_SIZE;

  float gyro_var = 0.0f;
  float lin_acc_var = 0.0f;

  for (int i = 0; i < WINDOW_SIZE; i++) {
    float dg = gyroWindow[i] - gyro_avg;
    float da = linAccWindow[i] - lin_acc_avg;
    gyro_var += dg * dg;
    lin_acc_var += da * da;
  }

  gyro_var /= WINDOW_SIZE;
  lin_acc_var /= WINDOW_SIZE;

  Serial.print(fgx, 4); Serial.print(",");
  Serial.print(fgy, 4); Serial.print(",");
  Serial.print(fgz, 4); Serial.print(",");
  Serial.print(lin_acc_mag, 4); Serial.print(",");
  Serial.print(gyro_mag, 4); Serial.print(",");
  Serial.print(gyro_diff, 4); Serial.print(",");
  Serial.print(lin_acc_diff, 4); Serial.print(",");
  Serial.print(gyro_avg, 4); Serial.print(",");
  Serial.print(gyro_var, 4); Serial.print(",");
  Serial.print(lin_acc_avg, 4); Serial.print(",");
  Serial.print(lin_acc_var, 6); Serial.print(",");
  Serial.print(lin_ax_avg, 4); Serial.print(",");
  Serial.print(lin_ay_avg, 4); Serial.print(",");
  Serial.println(lin_az_avg, 4);

  delay(10);
}