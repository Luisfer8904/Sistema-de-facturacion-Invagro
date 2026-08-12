ALTER TABLE `inva-cobros_personales`
  ADD COLUMN `cliente_id` INT NULL AFTER `numero_cobro`;

ALTER TABLE `inva-cobros_personales`
  ADD INDEX `idx_cliente_cobro_personal` (`cliente_id`);

ALTER TABLE `inva-cobros_personales`
  ADD CONSTRAINT `fk_cobro_personal_cliente`
  FOREIGN KEY (`cliente_id`) REFERENCES `inva-clientes`(`id`)
  ON DELETE SET NULL;
